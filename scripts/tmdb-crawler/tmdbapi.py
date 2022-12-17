import requests
from pymongo import MongoClient

api_key = '?api_key=aadbecbdb50376aab20b843948fdd76a&language=en-US'

base_url = "https://api.themoviedb.org/3/"


def get_database():
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    return client


def get_tmdb_live_db():
    return get_database()['tmdb-live']


def get_tmdb_meta_db():
    return get_database()['tmdb-meta']


def build_url(endpoint, params=""):
    url = base_url + endpoint + api_key
    if params != "":
        url = url + "&" + params
    return url


def search_movie(name):
    url = build_url("search/movie", f"query={name}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_movie_details(id):
    url = build_url(f"movie/{id}")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_movie_credits(id):
    url = build_url(f"movie/{id}/credits")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_popular():
    url = build_url("movie/popular")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_top_rated():
    url = build_url("movie/top_rated")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_genre_list():
    url = build_url("genre/movie/list")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def build_genre_list():
    genre_count = get_tmdb_live_db().genres.count_documents({})
    if genre_count == 0:
        list = get_genre_list()
        if list:
            get_tmdb_live_db().genres.insert_many(list['genres'])
            print("genres list updated")


def get_genre(id2):
    build_genre_list()
    genre = get_tmdb_live_db().genres.find({"id": id2}).limit(1)
    for doc in genre:
        return doc["name"]
    return ""

def get_language(code):
    lang = get_tmdb_live_db().languages.find({"code": code}).limit(1)
    for doc in lang:
        return doc["name"]
    return ""

def get_similar_movies(id2):
    url = build_url(f"movie/{id2}/similar")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


if __name__ == '__main__':
    print(search_movie("trimurti"))
