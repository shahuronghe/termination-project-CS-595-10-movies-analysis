import configparser
import html
from datetime import datetime
import re
import requests
from pymongo import MongoClient
import json
from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")
base_url = "https://www.reddit.com"


def build_search_url(sub, key, type2):
    return f"{base_url}/r/{sub.strip()}/search.json?q={key.strip()}&restrict_sr=on&sort={type2}&limit=25"


def get_reddit_comments(url):
    if url == "":
        return []
    headers = {'content-type': 'application/json', 'user-agent': 'cs-515-social_media-project'}
    response = requests.get(url, headers=headers)
    comments = []
    bundle = {}
    positives = 0
    negatives = 0
    neutrals = 0
    if response.status_code == 200:
        json_response = json.loads(response.content)
        if len(json_response) > 1:
            if 'data' in json_response[1] and 'children' in json_response[1]['data']:
                json_dict = json_response[1]['data']['children']
                for d in json_dict:
                    if "body" in d["data"] and len(comments) < 20:
                        com = {k: d['data'][k] for k in ("body", "ups", "downs")}
                        body = com["body"][:256]
                        if '[deleted]' == body:
                            continue
                        sentiment = sentiment_pipeline(body)
                        if len(sentiment) != 0:
                            label = sentiment[0]["label"]
                            if label == "POSITIVE":
                                positives += 1
                            elif label == "NEGATIVE":
                                negatives += 1
                            else:
                                neutrals += 1
                            com["label"] = label
                            com["score"] = str(sentiment[0]["score"])[:4]
                        comments.append(com)
    if len(comments) > 0:
        bundle["comments"] = comments
        bundle["overall_sentiments"] = {"positive": positives, "negative": negatives, "neutral": neutrals}
    return bundle


def query_reddit(url):
    headers = {'content-type': 'application/json', 'user-agent': 'cs-515-social_media-project'}
    response = requests.get(url, headers=headers)
    selected_fields = []
    if response.status_code == 200:
        json_response = json.loads(response.content)['data']['children']
        for d in json_response:
            comment_url = d['data']['permalink'] if 'permalink' in d['data'] else ""

            bundle = get_reddit_comments(base_url + comment_url + ".json")
            if len(bundle) == 0:
                continue
            post = {k: d['data'][k] for k in
                    ("selftext", "subreddit", "title", "num_comments", "downs", "ups", "total_awards_received",
                     "created_utc", "permalink")}
            post["comments"] = bundle["comments"]
            post["overall_senti"] = bundle["overall_sentiments"]
            post["permalink"] = base_url + post["permalink"]
            post["selftext"] = str(post["selftext"]).replace("***", "")
            post["selftext"] = html.unescape(str(post["selftext"])[:512])
            post["title"] = html.unescape(post["title"])
            selected_fields.append(post)
    return selected_fields


def get_sub_reddits():
    config = configparser.ConfigParser()
    config.read('/home/sronghe1/project1-impl/subreddits.ini')
    subreddits = config["SUBREDDITS"]["list"].split(",")
    return subreddits


def get_database():
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    return client


def get_twitter_db():
    return get_database()['twitter-data']


def get_reddit_db():
    return get_database()['reddit-data']


def dict2obj(d):
    if isinstance(d, list):
        d = [dict2obj(x) for x in d]
    if not isinstance(d, dict):
        return d

    class C:
        pass

    obj = C()
    for k in d:
        obj.__dict__[k] = dict2obj(d[k])
    return obj


def start():
    if get_twitter_db().tweets.count_documents({"visited": False}) == 0:
        print("No new tweets available in mongodb!\n")
        return
    unvisited_tweets = get_twitter_db().tweets.find({"visited": False})
    count = 0
    for doc in unvisited_tweets:
        count += 1
        x = dict2obj(doc)
        movie_name = str(x.title.split('(')[0])
        year2 = re.search(r'(\d{4})', x.title)
        year = str(year2.groups()[0]) if year2 else ""
        movie = movie_name + year
        if get_reddit_db().comments.count_documents({"title": movie_name + year}) == 0:
            print(movie_name + str(year))
            reddit_data = []
            for each in get_sub_reddits():
                results = query_reddit(build_search_url(each, movie_name, "new"))
                subreddits = {}
                if len(results) > 0:
                    subreddits["subreddit"] = each
                    subreddits["posts"] = results
                    reddit_data.append(subreddits)

            sentiment = sentiment_pipeline(x.text)[0]
            label = sentiment["label"]
            tweets = [{"tweet": x.text, "label": label, "timestamp": datetime.now()}]
            single = {"title": movie, "last_updated": datetime.now(),
                      "movie_desc": x.description, "url": x.main_url, "imdb_id": x.imdb_id, "tweets": tweets,
                      "subreddits": reddit_data}
            mongo_db = get_reddit_db()
            collection = mongo_db.comments
            collection.insert_one(single, bypass_document_validation=False, session=None, comment=None)
            print("inserted: " + movie)
        else:
            if x.text != "":
                sentiment = sentiment_pipeline(x.text)[0]
                label = sentiment["label"]
                tweet = {"tweet": x.text, "label": label, "timestamp": datetime.now()}
                col = get_reddit_db().comments
                col.find_one_and_update({"title": movie},
                                        {"$push": {"tweets": tweet}})
                print("Tweet updated: " + movie)

        col = get_twitter_db().tweets
        col.find_one_and_update({"_id": x._id},
                                {"$set": {"visited": True}})

    print("unvisited tweets: " + str(count))
    print()


if __name__ == '__main__':
    start()
