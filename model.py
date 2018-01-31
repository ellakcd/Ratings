"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation
# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """provide helpful representation when printed"""

        return "<User user_id={} email={}>".format(self.user_id,
                                               self.email)


# Put your Movie and Rating model classes here.

class Movie(db.Model):
    """Movie to rate."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    # release_date = db.Column(db.DateTime, nullable=False)
    video_release = db.Column(db.DateTime, nullable=True)
    IMDB = db.Column(db.String(150), nullable=True)
    # genres = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """provide helpful representation when printed"""

        return "<Movie movie_id={} title={} video_release, IMDB>".format(self.movie_id,
                                               self.title)

class Rating(db.Model):
    """Ratings"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.movie_id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    # timestamp = db.Column(db.datetime, nullable=False)

    user = db.relationship("User", backref=db.backref("ratings",
                                                        order_by=rating_id))

    movie = db.relationship("Movie",
                            backref=db.backref("ratings",
                                               order_by=rating_id))

    def __repr__(self):
        """provide helpful representation when printed"""

        return "<Rating movie_id={} rating={} rating_id, user_id>".format(self.movie_id,
                                           self.rating)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
