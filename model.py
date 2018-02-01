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

    def similarity(self, other):
        """Find the pearson correlation between self & other user"""
        # 1. {}
        # 2. [()]

        # go through all the ratings & add to dict w/ movie_id : rating
        # check if other user has rated the same movie,
        #     if yes, push pair into list of tuples


        # if the list exists,
        # pass list through pearson coeff,
        # if it is empty,
        #     else, return 0

        u_ratings = {}
        pairs = []

        for rating in self.ratings:
            u_ratings[rating.movie_id] = rating.rating

        for r in other.ratings:
            # print "I am other user's rating!!\n\n\n"
            # print r
            if r.movie_id in u_ratings.keys():
                pairs.append((u_ratings[r.movie_id], r.rating))

        if pairs:
            return correlation.pearson(pairs)
        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict how a user would rate a movie given movie object"""

        #how other users rated Toy Story
        other_ratings = movie.ratings

        # list of tuples, of (pearson coeff between me & user, user's rating)
        similarities = sorted([
            (self.similarity(r.user), r)
            for r in other_ratings
            if self.similarity(r.user) > 0
            ], reverse=True)

        # print self.email
        # import pdb; pdb.set_trace()
        if not similarities:
            return None

        # weighted mean/ predicted rating = sum(ratings * coeffs)/ sum(coeffs)
        numerator = sum([r.rating * sim for sim, r in similarities])
        denominator = sum([sim for sim, r in similarities])

        return numerator / denominator

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
