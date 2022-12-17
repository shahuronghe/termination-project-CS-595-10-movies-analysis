from pymongo import MongoClient

def get_database():
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    return client


def get_twitter_db():
    return get_database()['twitter-data']


def get_reddit_db():
    return get_database()['reddit-data']


tweets = get_twitter_db().tweets.count_documents({})
unv = get_twitter_db().tweets.count_documents({"visited":False})
tweet_size = get_twitter_db().command("dbstats")
print("tweets count: " + str(tweets) + " unvisited: " + str(unv) + ", size: " + str(round(float(tweet_size["storageSize"]/1000000),2)) + " MB")

comments_size = get_reddit_db().command("dbstats")
comments = get_reddit_db().comments.count_documents({})
print("reddit count: " + str(comments)  + ", size: " + str(round(float(comments_size["storageSize"]/1000000),2)) + " MB")

import subprocess
import os

pythonProcess = subprocess.check_output("ps ax | grep 'playground\|twitter'",shell=True).decode()
pythonProcess = pythonProcess.split('\n')

playground_running = False
twitter_running = False
for process in pythonProcess:
    if "python3 project1-impl/twitter-api/twitter_app.py" in process:
        twitter_running = True
        print("Twitter running, pid: "+process.split(" ")[0])

for process in pythonProcess:
    if "python3 project1-impl/playground.py" in process:
        playground_running = True
        print("playground running, pid: "+process.split(" ")[0])


if not twitter_running:
    print("twitter Process was not running, running it now!")
    os.system("nohup python3 project1-impl/twitter-api/twitter_app.py > run_output/twitter_output.log &")

if not playground_running:
    print("playground Process was not running, running it now!")
    os.system("nohup python3 project1-impl/playground.py > run_output/twitter_output.log &")


print("end")
print("\n")
