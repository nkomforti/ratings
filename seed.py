"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Movie, Rating

from model import connect_to_db, db
from server import app

import datetime


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # Add to the session to be stored.
        db.session.add(user)

    # Add to database.
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate movies.
    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip()
        movie_data = row.split("|")
        movie_id = movie_data[0]
        title = movie_data[1][:-7]  # Slice off parenthetical date in title.
        imdb_url = movie_data[4]

        released_str = movie_data[2]  # Save date string.

        # If date string (Truthy).
        if released_str:
            # Convert date string to datetime object, save to variable.
            released_at = datetime.datetime.strptime(released_str, "%d-%b-%Y")
        # Otherwise, make equal to None.
        else:
            released_at = None

        movie = Movie(movie_id=movie_id,
                      title=title,
                      released_at=released_at,
                      imdb_url=imdb_url)

        # Add to the session to be stored.
        db.session.add(movie)

    # Add to database.
    db.session.commit()


# def load_ratings():
#     """Load ratings from u.data into database."""

#     print "Ratings"

#     Rating.query.delete()
#     query = "SELECT setval('ratings_rating_id_seq', 1)"
#     db.session.execute(query)
#     db.session.commit()

#     for i, row in enumerate(open("seed_data/u.data")):
#         row = row.rstrip()

#         user_id, movie_id, score, timestamp = row.split("\t")

#         user_id = int(user_id)
#         movie_id = int(movie_id)
#         score = int(score)

#         # We don't care about the timestamp, so we'll ignore this

#         rating = Rating(user_id=user_id,
#                         movie_id=movie_id,
#                         score=score)

#         # We need to add to the session or it won't ever be stored
#         db.session.add(rating)

#         # provide some sense of progress
#         if i % 1000 == 0:
#             print i

#             # An optimization: if we commit after every add, the database
#             # will do a lot of work committing each record. However, if we
#             # wait until the end, on computers with smaller amounts of
#             # memory, it might thrash around. By committing every 1,000th
#             # add, we'll strike a good balance.

#             db.session.commit()

#     # Once we're done, we should commit our work
#     db.session.commit()


# NOTE: This version of load_ratings does not work. WIP.
def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate ratings.
    Rating.query.delete()
    query = "SELECT setval('ratings_rating_id_seq', 1)"
    db.session.execute(query)
    db.session.commit()

    for row in open("seed_data/u.data"):
        row = row.rstrip()
        rating_data = row.split("\t")

        user_id = rating_data[0]
        movie_id = rating_data[1]
        score = rating_data[2]

        rating = Rating(movie_id=movie_id,
                        user_id=user_id,
                        score=score)
        # Add to the session to be stored.
        db.session.add(rating)

    # Add to database.
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
    # We are adjusting the users_user_id_seq, using the Postgres function setval.
    set_val_user_id()
