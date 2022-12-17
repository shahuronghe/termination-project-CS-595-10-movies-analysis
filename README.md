## Project Abstract

The data that we have collected since October 2022 is enough for analysis of Trending Movies. We have collected huge
amount of data from Twitter, Reddit and TMDB to build analysis on movies and their reviews. In this part of project, we
have added many analysis such as Top Ten Movies by Rating, Top Ten Movies by Popularity, Top Ten Cast, Top Ten Genres,
Top Ten Directors, Top Ten Movies From Twitter & Reddit, Worst Movies From Twitter & Reddit, Most Negative Movies
Tweets, Most Negative Movies Comments, Most Positive Movies Tweets and Most Positive Movies Comments. With that, we have
added a checked button which will retrieve the movies which are release in this year only. We have date filters with
which we get movies/actors/directors named as start and end date. After collecting all these filter, we can generate
plots and can see the different plots. Also added extra functionality to search actor, movie, director and genre which will list the movies with poster and rating. Movie detail view provides more information about the movie such as rating, popularity, tweets, reddit comments, similar movies.

## Team
* Shahu Ronghe, sronghe1@binghamton.edu

## Tech-stack

* `python` - The project is developed and tested using python v3.8. [Python Website](https://www.python.org/)
* `request` - Request is a popular HTTP networking module(aka library) for python programming
  language. [Request Website](https://docs.python-requests.org/en/latest/#)
* `MongoDB`- This project uses NoSQL for saving collected data.
    * [MongoDB Website](https://www.mongodb.com/)
    * [Python MongoDB Adapter - pymongo](https://pymongo.readthedocs.io/en/stable/)
* `datetime` - The datetime module supplies classes for manipulating dates and
  times. [datetime Website](https://docs.python.org/3/library/datetime.html/)
* `matplotlib` - matplotlib is used for plotting the graphs and bar
  charts. [matplotlib Website](https://matplotlib.org/)
* `flask` - We have developed our webapp with flask which provides many
  functionalities. [Flask Website](https://flask.palletsprojects.com/)
* `base64` - This module provides functions for encoding binary data to printable ASCII characters and decoding such
  encodings back to binary data. [base64](https://docs.python.org/3/library/base64.html)
* `itertools` - Python’s Itertool is a module that provides various functions that work on iterators to produce complex
  iterators. This module works as a fast, memory-efficient tool that is used either by themselves or in combination to
  form iterator algebra. [itertools](https://docs.python.org/3/library/itertools.html)
* `OrderedDict` - An OrderedDict is a dictionary subclass that remembers the order that keys were first
  inserted. [OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
* `itemgetter` - Return a callable object that fetches item from its operand using the operand's __getitem__()
  method. [itemgetter](https://docs.python.org/3/library/operator.html)
* `BytesIO` = Binary I/O (also called buffered I/O) expects bytes-like objects and produces bytes
  objects. [BytesIO](https://wiki.python.org/moin/BytesIO)

## Three data-source documentation

* `Twitter`
    * [Twitter Filtered Stream API](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction)
      - The filtered stream endpoint group enables developers to filter the real-time stream of public Tweets. This
      endpoint group’s functionality includes multiple endpoints that enable you to create and manage rules, and apply
      those rules to filter a stream of real-time Tweets that will return matching public Tweets.
* `Reddit` - We are using `Movies, badMovies, NetflixBestOf, MovieDetails` which is mentioned in subreddits.ini (config
  file) can be modified at any time.
    * [r/Movies](https://reddit.com/r/Movies) - The goal of /r/Movies is to provide an inclusive place for discussions
      and news about films with major releases.
    * [r/badMovies](https://reddit.com/r/badMovies) - The official subreddit for the celebration of movies that are so
      bad, they're good.
    * [r/NetflixBestOf](https://reddit.com/r/NetflixBestOf) - The primary purpose of /r/NetflixBestOf is to shitpost
      about Breaking Bad.
    * [r/MovieDetails](https://reddit.com/r/MovieDetails) - Details in Movies, Movie Details!
* `tmdb` - The API service is for those of you interested in using our movie, TV show or actor images and/or data in
  your application. Our API is a system we provide for you and your team to programmatically fetch and use our data
  and/or images.
    * [API-Link](https://developers.themoviedb.org/3) - Several API are provided to fetch details of movies.
    * [Website-link](https://www.themoviedb.org/) - the movie database similar to IMDB.

## System Architecture
for collecting data from Twitter, Reddit and TMDB:
![System Architecture](https://drive.google.com/uc?export=view&id=1U5ZcVlE-9_gzfyvOr8DqQEYZIuAmuzzw)

Dashboard flow:
![pro3-syst-arch drawio](https://user-images.githubusercontent.com/90294806/208221918-3600944b-5d2f-4aa8-bd21-d7952eebb87b.png)


## How to run the project?

Install `Python3` and `MongoDB`
[MongoDB Installation Link] (https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)

```bash
#start the flask web server
clone git@github.com:shahuronghe/termination-project-CS-595-10-movies-analysis.git
pip install -r requirements.txt
cd termination-project-CS-595-10-movies-analysis
python3 app.py

#access the webapp
#You can either access it using the VMs UI or can port forward your current laptop OS.
#for port forwading, enter this command into your local terminal.
ssh -L 5001:127.0.0.1:5001 sronghe1@128.226.28.127
#open web brower on your laptop and enter this URL
http://127.0.0.1:5001/
```

## Database schema - NoSQL

```bash
db: twitter-data
collection_1: tweets
{
  "id": ...,
  "title": ...,
  "description": ...,
  "text": ...,
  "main_url": ...,
  "imdb_id": ...,
  "last_updated": ...,
}

db: reddit-data
collection_2: comments
{
  "id": ...,
  "last_updated": ...,
  "movie_desc": ...,
  "url": ...,
  "imdb_id": ...,
  "tweets": [],
  "subreddits": [ "posts": ["comments":[]]]]
}

db: tmdb-live
collection_3: daily
{
  "id": ...,
  "timestamp": ...,
  "popular": [],
  "top_rated": []
}

db: tmdb-meta
collection_4: map
{
  "id": ...,
  "title": ...,
  "actors": ...,
  "directors": ...,
  "genre": ...,
  "negative_comments": [],
  "positive_comments": [],
  "popularity": ...,
  "rating": ...,
  "timestamp": ...
}
```
