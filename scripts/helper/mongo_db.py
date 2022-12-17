from pymongo import MongoClient

def get_database():
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    return client

def get_reddit_db():
    return get_database()['reddit-data']

def get_twitter_db():
    return get_database()['twitter-data']

def get_tmdb_db():
    return get_database()['tmdb-data']