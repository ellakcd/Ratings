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

    user_info = db.session.query(User.email, User.password).all()

    email = request.form.get("email")
    password = request.form.get("password")
    user = (email, password)

    if user in user_info:
        session['current_user'] = email
        flash('Successfully logged in as {}'.format(email))
    else:
        flash("Begone imposter!!")

    return redirect("/")

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
