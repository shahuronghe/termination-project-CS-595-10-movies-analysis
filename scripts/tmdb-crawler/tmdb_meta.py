# this script is for aggregating the data from all three data sources into one collection
from tmdbapi import search_movie, get_genre, get_movie_credits, get_language, get_similar_movies
import re
import itertools
from db import get_reddit_db, get_tmdb_meta_db


def get_comments(subreddits):
    positive_comments = {}
    negative_comments = {}
    for subr in subreddits:
        posts = subr["posts"]
        for p in posts:
            comments = p["comments"]
            for c in comments:
                label = c["label"]
                comm = c["body"]
                if label == "NEGATIVE":
                    ups = c["ups"]
                    negative_comments[comm] = ups
                if label == "POSITIVE":
                    ups = c["ups"]
                    positive_comments[comm] = ups
    if len(positive_comments) < 5 or len(negative_comments) < 5:
        return {}, {}
    positive_comments = dict(sorted(positive_comments.items(), key=lambda item: item[1]))
    negative_comments = dict(sorted(negative_comments.items(), key=lambda item: item[1]))
    positive_comments = dict(
        itertools.islice(positive_comments.items(), len(positive_comments) - 5, len(positive_comments)))
    negative_comments = dict(
        itertools.islice(negative_comments.items(), len(negative_comments) - 5, len(negative_comments)))
    return positive_comments, negative_comments


def update_map():
    reddit = get_reddit_db().comments.find({"visited": {"$exists":False}})
    for mov in reddit:
        get_reddit_db().comments.update_one(mov, update={"$set": {"visited": True}})
        title = mov["title"]
        release_date = ''
        url = mov["url"]
        tweet_count = len(mov["tweets"]) if "tweets" in mov else 0
        neg_tweet = 0
        pos_tweet = 0
        neu_tweet = 0
        neg_tweets_text = []
        pos_tweets_text = []
        neu_tweets_text = []
        timestamp = mov["last_updated"]
        for t in mov["tweets"]:
            label = t["label"]
            text = t["tweet"]
            if label == "NEGATIVE":
                neg_tweet += 1
                neg_tweets_text.append(text)

            if label == "POSITIVE":
                pos_tweet += 1
                pos_tweets_text.append(text)

            if label == "NEUTRAL":
                neu_tweet += 1
                neu_tweets_text.append(text)

        pos_comm, neg_comm = get_comments(mov["subreddits"])
        if len(pos_comm) == 0 or len(neg_comm) == 0:
            continue

        year2 = re.search(r'(\d{4})', title)
        year = str(year2.groups()[0]) if year2 else ""
        title = title.rsplit(' ', 1)[0]

        meta = search_movie(title)
        if meta is None:
            continue
        meta = meta["results"]
        movie = {}
        if len(meta) > 0:
            if year != "":
                for m in meta:
                    if "release_date" in m:
                        release_date = m["release_date"]
                        rel_year = m["release_date"].split("-")[0]
                        if year == rel_year:
                            movie = m
                            break
            else:
                if len(meta) > 0:
                    movie = meta[0]
        genre_list = ""
        sep = ""
        if "id" not in movie:
            continue
        mov_id = movie["id"]
        for gen in movie["genre_ids"]:
            genre_list += sep + get_genre(gen)
            sep = ", "
        mov_creds = get_movie_credits(mov_id)
        cast = mov_creds["cast"]
        crew = mov_creds["crew"]
        sep = ""
        actors = ""
        i = 0
        for c in cast:
            if c["known_for_department"] == "Acting":
                i += 1
                actors += sep + c["name"]
                sep = ", "
            if i == 5:
                break
        sep = ""
        director = ""
        i = 0
        for c in crew:
            if c["known_for_department"] == "Directing" and c["department"] == "Directing":
                i += 1
                director += sep + c["name"]
                sep = ", "
            if i == 5:
                break
        if "poster_path" not in movie or movie["poster_path"] is None:
            poster = "<not found>"
        else:
            poster = movie["poster_path"]
        language = get_language(movie['original_language'])

        final = {"title": title, "overview": movie["overview"], "actors": actors, "directors": director,
                 "genre": genre_list, "poster": "https://image.tmdb.org/t/p/original" + poster,
                 "rating": movie["vote_average"], "popularity": movie["popularity"], "timestamp": timestamp,
                 "negative_comments": neg_comm, "positive_comments": pos_comm, "positive_tweets_count": pos_tweet,
                 "positive_tweets_text": pos_tweets_text, "negative_tweets_count": neg_tweet,
                 "negative_tweets_text": neg_tweets_text, "release_year": rel_year, "tweets_count": tweet_count,
                 "imdb_link": url, "release_date": release_date, "vote_count": movie["vote_count"],
                 "lang": language, "tmdb_id": mov_id}

        print("inserted: ")
        get_tmdb_meta_db().map.update_one(filter={"title": title}, update={"$set": final},
                                          upsert=True)
        print(final)
        if str(release_date) != '':
            rel_split = release_date.split("-")
            if rel_split[0] == "2022":
                get_tmdb_meta_db().map.update_one(filter={"title": title}, update={"$set": {"2022": True}},
                                                  upsert=True)


def update_cast_crew():
    cast_crew = get_tmdb_meta_db().map.find({"visited": {"$exists": False}}, {"actors": 1, "directors": 1})
    for cc in cast_crew:
        get_tmdb_meta_db().map.update_one(cc, update={"$set": {"visited": True}})
        if "actors" not in cc or "directors" not in cc:
            continue
        cast = cc["actors"].split(",")
        crew = cc["directors"].split(",")
        mov_id = cc["_id"]

        for c in cast:
            doc = {"name": c.strip(), "dept": "acting"}
            get_tmdb_meta_db().cast_crew.update_one(filter=doc, update={"$set": doc, "$push": {"movies": mov_id}},
                                                    upsert=True)

        for c in crew:
            doc = {"name": c.strip(), "dept": "director"}
            get_tmdb_meta_db().cast_crew.update_one(filter=doc, update={"$set": doc, "$push": {"movies": mov_id}},
                                                    upsert=True)

    print("Cast and Crew Updated!")


if __name__ == '__main__':
    update_map()
    update_cast_crew()
