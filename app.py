from flask import Flask, render_template, request, jsonify, send_from_directory,url_for
import os
import json

from data_processing import alter_movie_obj, clean_review_comments,    get_movie_results
from db import get_tmdb_meta_db, get_tmdb_live_db

app = Flask(__name__)
from plot_movies import collect_data
from flask_cors import CORS
from bson.objectid import ObjectId
from tmdbapi import get_similar_movies, get_movie_details, get_movie_credits

CORS(app)

search_list2 = []


def json_response_on_error():
    d = {"result": "failed"}
    response = app.response_class(
        response=json.dumps(d, indent=4, sort_keys=True, default=str),
        status=200
    )
    return response


def json_response_on_success(d):
    response = app.response_class(
        response=json.dumps(d, indent=4, sort_keys=True, default=str),
        status=200
    )
    return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'static/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/trends')
def trend_home():
    return render_template('homepage.html')


@app.route("/similar", methods=['GET'])
def get_similar_movies2():
    args = request.args
    if len(args) == 0:
        return json_response_on_error()
    movie_id = args.get("movie_id")
    return json_response_on_success(get_similar_movies(movie_id)["results"])


@app.route("/plot_movies", methods=['POST'])
def plot_movies_by_date():
    date1 = request.form['date_1']
    date2 = request.form['date_2']
    type = request.form['movie_filter']
    this_year = "disable"
    if '2022_flag' in request.form:
        this_year = request.form['2022_flag']
    plot_url = collect_data(date1, date2, type, this_year)
    return render_template('plot_image.html', plot_url=plot_url)


@app.route("/search_list", methods=["GET"])
def search_list():
    return json_response_on_success(search_list2)


@app.route("/get_movie_details", methods=["GET"])
def get_details():
    global movie
    args = request.args
    if len(args) == 0:
        return render_template("movie_details.html")
    movie_id = args.get("movie_id")
    if len(movie_id) != 24:
        db_movie = get_tmdb_meta_db().map.find({"tmdb_id": int(movie_id)}).limit(1)
        found_in_db = False
        for dm in db_movie:
            movie = dm
            found_in_db = True
        if not found_in_db:
            movie = get_movie_details(movie_id)
            movie = alter_movie_obj(movie)
    else:
        movie = get_tmdb_meta_db().map.find({"_id": ObjectId(movie_id)}).next()

    movie = clean_review_comments(movie)
    return render_template('movie_details.html', movie=movie)


@app.route("/get_results", methods=['POST'])
def get_results2():
    param1 = str(request.json["search"]).rsplit("-", 1)
    print(param1)
    search_str = param1[0].strip()
    type2 = param1[1].strip()
    res_list = get_movie_results(type2, search_str)

    if len(res_list) == 0:
        return json_response_on_error()
    res_list = sorted(res_list, key=lambda x: x['rating'], reverse=True)
    return json_response_on_success(res_list)


if __name__ == '__main__':
    tmdb_cast_crew = get_tmdb_meta_db().cast_crew.find({}, {"name": 1, "dept": 1})
    tmdb_map = get_tmdb_meta_db().map.find({}, {"title": 1})
    tmdb_genre = get_tmdb_live_db().genres.find({}, {"name": 1})

    for cc in tmdb_cast_crew:
        combine = cc["name"] + " - " + cc["dept"]
        search_list2.append(combine)

    for mov in tmdb_map:
        combine = mov["title"] + " - movie"
        search_list2.append(combine)

    for g in tmdb_genre:
        combine = g["name"] + " - genre"
        search_list2.append(combine)

    search_list2.sort()
    app.run(host='127.0.0.1', port=5001, debug=True)
