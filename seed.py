"""Utility file to seed ratings database from MovieLens data in seed_data/"""

import datetime
from sqlalchemy import func
from model import User, Movie, Rating
# from model import Rating
# from model import Movie

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    with open("seed_data/u.user") as users:
        for row in users:
            row = row.rstrip()
            user_id, age, gender, occupation, zipcode = row.split("|")

            user = User(user_id=user_id,
                        age=age,
                        zipcode=zipcode)

            # We need to add to the session or it won't ever be stored
            db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    Movie.query.delete()

    with open("seed_data/u.item") as movies:
        for row in movies:
            row = row.rstrip()
            movie_attributes = row.split("|")
            movie_id = movie_attributes[0]
            title = movie_attributes[1][:-7].decode("latin-1")
            video_release = movie_attributes[2]
            if video_release:
                video_release = datetime.datetime.strptime(video_release, "%d-%b-%Y")
            else:
                video_release = None
            imdb = movie_attributes[4]

            movie = Movie(movie_id=movie_id,
                    title=title,
                    video_release=video_release,
                    IMDB=imdb
                    )
            db.session.add(movie)
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    Rating.query.delete()

    with open("seed_data/u.data") as ratings:
        for row in ratings:
            row = row.rstrip()
            user_id, movie_id, rating, timestamp = row.split("\t")

            rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        rating=rating
                        )

            db.session.add(rating)
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
