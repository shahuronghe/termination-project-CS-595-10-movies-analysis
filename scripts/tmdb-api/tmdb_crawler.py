from tmdb_lib import get_popular, get_top_rated, get_tmdb_live_db

from datetime import datetime


def run():
    now = datetime.now()
    whats_popular = get_popular()['results']
    top_rated = get_top_rated()['results']
    today = {"popular": whats_popular, "top-rated": top_rated, "timestamp": now}
    get_tmdb_live_db().daily.insert_one(today, bypass_document_validation=False, session=None, comment=None)

    print(today)
    print("inserted at " + str(now))



if __name__ == '__main__':
    run()
