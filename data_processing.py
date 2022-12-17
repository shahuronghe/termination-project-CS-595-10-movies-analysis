from tmdbapi import get_movie_credits, get_language
from db import get_tmdb_meta_db


def get_movie_results(type2, search_str):
    res_list = []
    if type2 == "movie":
        res_list.append(get_tmdb_meta_db().map.find({"title": search_str}).next())

    if type2 == "genre":
        res = get_tmdb_meta_db().map.find({"genre": {"$regex": search_str}})
        for r in res:
            res_list.append(r)

    if type2 == "acting" or type2 == "director":
        res = get_tmdb_meta_db().cast_crew.find({"name": search_str, "dept": type2})
        mov_list = res.next()["movies"]
        for m in mov_list:
            query = {"_id": m}
            mov_list2 = get_tmdb_meta_db().map.find(query)
            for m2 in mov_list2:
                res_list.append(m2)

    return res_list


def get_cast_crews(id2):
    mov_creds = get_movie_credits(id2)
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
    return actors, director


def alter_movie_obj(movie):
    id2 = movie["id"]
    actors, directors = get_cast_crews(id2)
    movie["actors"] = actors
    movie["directors"] = directors
    genres = movie["genres"]
    genres_list = ', '.join(d["name"] for d in genres)
    movie["genre"] = genres_list
    movie["poster"] = "https://image.tmdb.org/t/p/original" + movie.pop("poster_path")
    movie["tmdb_id"] = movie.pop("id")
    movie["imdb_link"] = "https://www.imdb.com/title/" + movie.pop("imdb_id")
    movie["lang"] = get_language(movie['original_language'])
    movie["rating"] = round(movie.pop("vote_average"), 1)
    movie["no_review"] = True
    return movie


import re


def clean(s):
    temp = s.lower()
    temp = re.sub("@[A-Za-z0-9_]+", "", temp)
    temp = re.sub(r"http\S+", "", temp)
    temp = re.sub(r"www.\S+", "", temp)
    temp = re.sub('[()!?]', ' ', temp)
    temp = re.sub('\[.*?\]', ' ', temp)
    # temp = re.sub("[^'a-z0-9]", " ", temp)
    return temp


def clean_review_comments(m):
    print("before", m)

    if "negative_comments" in m:
        l1 = m["negative_comments"]
        m["negative_comments"] = {clean(i): x for i, x in l1.items()}

    if "positive_comments" in m:
        l1 = m["positive_comments"]
        m["positive_comments"] = {clean(i): x for i, x in l1.items()}

    if "negative_tweets_text" in m:
        l1 = m["negative_tweets_text"]
        m["negative_tweets_text"] = [clean(item) for item in l1]

    if "positive_tweets_text" in m:
        l1 = m["positive_tweets_text"]
        m["positive_tweets_text"] = [clean(item) for item in l1]
    print("after", m)
    return m
