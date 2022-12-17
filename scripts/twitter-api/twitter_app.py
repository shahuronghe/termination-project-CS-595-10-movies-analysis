from types import SimpleNamespace
import json
from datetime import datetime
from datetime import date
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup


def get_html_title(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
    }
    reqs = requests.get(link, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    build_title = ""
    sep = ""
    for title in soup.find_all('title'):
        build_title = build_title + sep + title.get_text()
        sep = " * "
    return build_title


def get_imdb_id(link):
    return link.split("/")[4]


def get_database():
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    return client


def get_twitter_db():
    return get_database()['twitter-data']


bearer_token = 'AAAAAAAAAAAAAAAAAAAAABFphwEAAAAAVH9BAyXj9L1%2FpKQq13rXTU63Y4k%3DxNnOsN7CwNcjoQcVKNbsqZyvHinT9TgtcxvBzpAvbXn3kRtFzU'


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampleStreamPython"
    return r


def get_stream():
    url = "https://api.twitter.com/2/tweets/sample/stream?tweet.fields=entities,geo,lang,text&media.fields=url"
    payload = {"lang": "en"}
    response = requests.get(url, auth=bearer_oauth, stream=True, json=payload)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception("Cannot get stream (HTTP {}): {}".format(response.status_code, response.text))
    for response_line in response.iter_lines():
        if response_line:
            x = json.loads(response_line, object_hook=lambda d: SimpleNamespace(**d))
            if hasattr(x, "data") and x.data.lang == "en":
                insert_into_db(x.data)


def update_metadata(key):
    today = str(date.today())
    stats = get_twitter_db()["stats"]
    filter2 = {"date": today}
    values = {"$inc": {key: 1}}
    stats.update_one(filter2, values, upsert=True)


def insert_into_db(data):
    update_metadata("total")
    time = datetime.now()
    if hasattr(data.entities, 'urls') and hasattr(data.entities.urls[0], 'expanded_url'):
        expanded_url = str(data.entities.urls[0].expanded_url)
        print(expanded_url)
        if expanded_url.startswith("https://www.imdb.com/title/") or expanded_url.startswith(
                "https://m.imdb.com/title/"):
            url_obj = data.entities.urls[0]
            title = url_obj.title if hasattr(url_obj, "title") else get_html_title(url_obj.expanded_url)
            if "TV" in title:
                pass
            else:
                imdb_id = get_imdb_id(url_obj.expanded_url)
                imdb_id = imdb_id if str(imdb_id).startswith("tt") else ""
                desc = url_obj.description if hasattr(url_obj, "description") else ""
                single = {"title": title, "description": desc, "main_url": url_obj.expanded_url,
                          "text": data.text, "visited": False, "imdb_id": imdb_id, "last_updated": time}

                mongo_db = get_twitter_db()
                collection = mongo_db.tweets
                print(single)
                update_metadata("useful")
                collection.insert_one(single, bypass_document_validation=False, session=None, comment=None)


if __name__ == "__main__":
    get_stream()
