"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<int:user_id>')
def user_info(user_id):
    """query database for user info to display"""

    user = User.query.get(user_id)
    movies = Rating.query.filter(Rating.user_id==user_id).all()

    return render_template("user_details.html", user=user, movies=movies)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = sorted(db.session.query(Movie.title, Movie.movie_id).all())
    return render_template("movie_list.html", movies=movies)

@app.route('/movies/<int:movie_id>')
def movie_info(movie_id):
    """query database for movie info to display
    If user is logged in, allow edit/add rating
    Give predictive rating
    """

    movie = Movie.query.get(movie_id)
    ratings = (Rating.query
              .filter(Rating.movie_id==movie_id)
              .order_by(Rating.user_id).all())

    # check if user is logged in & has rating data
    user_id = session.get("current_user")

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()
    else:
        user_rating = None


    # list of all the ratings for this movie
    rating_scores = [r.rating for r in movie.ratings]
    avg_rating = float(sum(rating_scores))/ len(rating_scores)

    prediction = None

    # prediction

    if (not user_rating) and user_id:
        # if user not rated, we predict
        user = User.query.get(user_id)
        prediction = user.predict_rating(movie)

    display = None

    if user_rating:
        display = user_rating.rating

    le_eye = (User.query.filter_by(email="theeye@ofjudgment.com").one())
    judgment = Rating.query.filter_by(
        user_id=le_eye.user_id, movie_id=movie.movie_id).first()

    if not judgment:
        judgment = le_eye.predict_rating(movie)
    else:
        judgment = judgment.rating

    difference = None
    if judgment and display:
        difference = abs(judgment - display)

    BERATEMENT_MESSAGES = [
     "You don't disgust me, only mildly distasteful.",
     "Roses are red, violets are blue.  Your movie taste sucks.",
     "Your taste in movies reminds me of Melania Trump's taste in men.",
     "I would rather watch paint dry, than a movie you like.",
     "I enjoy your opinion as much as I enjoy being poked in the eye slowly and repetitively."
    ]

    if difference >= 0:
        beratement = BERATEMENT_MESSAGES[int(difference)]
    else:
        beratement = None

    return render_template("movie_details.html",
                            movie=movie,
                            ratings=ratings,
                            average=avg_rating,
                            prediction=prediction,
                            beratement=beratement,
                            judgment=judgment
                            )


@app.route('/add_rating', methods=['POST'])
def add_rating():
    """add rating to database"""
    movie_id = request.form['movie_id']
    new_rating = request.form['rating']
    user_id = session["current_user"]

    try:
        rating = Rating.query.filter(Rating.movie_id==movie_id,
                                  Rating.user_id==user_id).one()
        rating.rating = new_rating
    except:
        db.session.add(Rating(user_id=user_id,
                        movie_id=movie_id,
                        rating=new_rating
                        ))

    db.session.commit()


    return redirect("/movies/{}".format(movie_id))

@app.route("/register", methods=['POST'])
def create_new_user():
    """Register new user."""

    email = request.form.get("email")
    password = request.form.get("password")

    if db.session.query(User.email).filter_by(email=email).first():
        flash("You've already signed up, silly!")
    else:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

    return redirect("/")

@app.route("/login", methods=['POST'])
def login():
    """Log In user."""

## FIX THIS LATER IF WE HAVE TIME, GHETTO CODEEEE

    user_info = db.session.query(User.email, User.password).all()

    email = request.form.get("email")
    password = request.form.get("password")
    user = (email, password)

    user_id = db.session.query(User.user_id).filter(User.email == email).one()[0]

    if user in user_info:
        session['current_user'] = user_id
        flash('Successfully logged in as {}'.format(email))
        return redirect("/users/{}".format(user_id))
    else:
        flash("Begone imposter!!")


@app.route("/logout")
def logout():
    """Log Out user."""

    del session['current_user']
    flash('Successfully logged out')

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
