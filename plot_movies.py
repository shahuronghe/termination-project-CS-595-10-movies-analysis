from db import get_tmdb_meta
from datetime import datetime
import base64
import itertools
from collections import OrderedDict
from operator import itemgetter
from io import BytesIO
import matplotlib.pyplot as plt

def get_top_items(d):
    sorted2 = OrderedDict(sorted(d.items(), key=itemgetter(1), reverse=True)).items()
    return dict(itertools.islice(sorted2, 10))


def generate_plot(data, headline, yaxis, date1, date2):
    title = []
    for label in data.keys():
        label2 = label.split(" ")
        i = 0
        t = ""
        for l in label2:
            t = t + l + " "
            i += 1
            if i % 4 == 0 and i < len(label2):
                t = t + "\n"

        title.append(t)
    data_pts = list(data.values())
    
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("From " + date1 + " to " + date2)
    plt.ylabel(yaxis, rotation=90)
    plt.bar(title, data_pts, color='teal',
            width=0.5)

    plt.title(headline)
    plt.tight_layout()
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.show()
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url


def collect_data(date1, date2, filter2, this_year):
    start = str(date1).split("-")
    end = str(date2).split("-")
    s1, s2, s3 = int(start[0]), int(start[1]), int(start[2])
    e1, e2, e3 = int(end[0]), int(end[1]), int(end[2])
    if date1 == date2:
        e3 += 1
    date_filter = {"timestamp": {"$gte": datetime(s1, s2, s3),
                                 "$lt": datetime(e1, e2, e3)}}
    if this_year == "enable":
        date_filter["2022"] = True
    data = {}
    headline = ""
    yaxis_label = ""

    if filter2 == "1":
        res = get_tmdb_meta().find(date_filter).sort("rating", -1).limit(10)
        for r in res:
            title = r["title"]
            rating = r["rating"]
            data[title] = rating
            headline = "Top Ten Movies by Rating"
            yaxis_label = "ratings"

    if filter2 == "2":
        res = get_tmdb_meta().find(date_filter).sort("popularity", -1).limit(10)
        for r in res:
            title = r["title"]
            rating = r["popularity"]
            data[title] = rating
        headline = "Top Ten Movies by Popularity"
        yaxis_label = "popularity"

    if filter2 == "3":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            actors = r["actors"].split(",")
            for act in actors:
                if act.strip() != "":
                    if act.strip() not in data:
                        data[act.strip()] = 1
                    else:
                        data[act.strip()] += 1
        data = get_top_items(data)
        headline = "Top Ten Cast"
        yaxis_label = "num of movies"

    if filter2 == "4":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            actors = r["genre"].split(",")
            for act in actors:
                if act.strip() != "":
                    if act.strip() not in data:
                        data[act.strip()] = 1
                    else:
                        data[act.strip()] += 1
        data = get_top_items(data)
        headline = "Top Ten Genres"
        yaxis_label = "num of movies"

    if filter2 == "5":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            actors = r["directors"].split(",")
            for act in actors:
                if act.strip() != "":
                    if act.strip() not in data:
                        data[act.strip()] = 1
                    else:
                        data[act.strip()] += 1
        data = get_top_items(data)
        headline = "Top Ten Directors"
        yaxis_label = "num of movies"

    if filter2 == "6":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            title = r["title"]
            comm = r["positive_comments"]
            ups = 0
            for c in comm:
                ups += comm[c]
            data[title] = r["positive_tweets_count"] + ups
        data = get_top_items(data)
        headline = "Top Ten Movies From Twitter & Reddit"
        yaxis_label = "num of positive reviews"

    if filter2 == "7":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            title = r["title"]
            comm = r["negative_comments"]
            ups = 0
            for c in comm:
                ups += comm[c]
            data[title] = r["negative_tweets_count"] + ups
        data = get_top_items(data)
        headline = "Worst Movies From Twitter & Reddit"
        yaxis_label = "num of negative reviews"

    if filter2 == "8":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            title = r["title"]
            data[title] = r["negative_tweets_count"]
        data = get_top_items(data)
        headline = "Most Negative Movies Tweets"
        yaxis_label = "num of negative tweets"

    if filter2 == "9":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            title = r["title"]
            comm = r["negative_comments"]
            ups = 0
            for c in comm:
                ups += comm[c]
            data[title] = ups
        data = get_top_items(data)
        headline = "Most Negative Movies Comments"
        yaxis_label = "num of negative comments"

    if filter2 == "10":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            title = r["title"]
            data[title] = r["positive_tweets_count"]
        data = get_top_items(data)
        headline = "Most Positive Movies Tweets"
        yaxis_label = "num of positive tweets"

    if filter2 == "11":
        res = get_tmdb_meta().find(date_filter)
        for r in res:
            title = r["title"]
            comm = r["positive_comments"]
            ups = 0
            for c in comm:
                ups +=comm[c]
            data[title] = ups
        data = get_top_items(data)
        headline = "Most Positive Movies Comments"
        yaxis_label = "num of positive comments"

    return generate_plot(data, headline, yaxis_label, date1, date2)
