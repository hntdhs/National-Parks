import os
import pdb

from flask import Flask, redirect, render_template, flash, url_for, request, session, g
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User
from forms import NewUserForm, LoginForm, UserEditForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///parks'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


connect_db(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    """first page user sees, allows user to either sign up or log in"""

    if g.user:
        return render_template('logged_in_home.html')

    else:
        return render_template('no_user_home.html')

@app.route('/national-parks', methods=["GET"])
def getNationalParks():
    """
        - Hits the external API to get all the parks
        - Filter the parks to only include National Parks
        - Return the National Parks
    """
    return 'Works!'

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = NewUserForm()
    if form.validate_on_submit():
        # try:
        user = User.signup(
           username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            )
        
        # pdb.set_trace()

        db.session.commit()

        # except IntegrityError:
        #     flash("Username already taken", 'danger')
        #     return render_template('users/signup.html', form=form)
        # ***********************

        do_login(user)

        return redirect("/parks")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            # return render_template('logged_in_home.html')
            # the logged in home template was going to have all the parks showing, but that's an API call, which doesn't happen in a template. So I should do the API call here and pass into the template? Or would it be easier to just have a link to see all the parks on logged_in_home?
            # redirect to url that's logged in homepage and that would have api call
            # login is good for redirect,
            return redirect("/parks")

        flash("Username and/or password are incorrect", 'danger')
        # how is this different from the return render_templatee('/login') right below - isn't that what happens if login info is incorrect? why was this in the form.validate_on_submit section? does it just go there when it hits the breakpoint below? 
        breakpoint()

    return render_template('/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    do_logout()

    flash("you have logged out", 'success')
    return redirect("/login")


# @app.route('/parks')
# def show_parks():
#     # api call to show parks
#     # render template logged_in_home, parks=parks


# @app.route('/parks/<int:park_id>')
# def park_info(park_id):
#     park = Park.query.get_or_404(park_id)
#     # api call needed to get park info


# @app.route('/favorite_parks')
# def show_favorites():
#     # query the database to find any parks the user has favorited, otherwise show message that they haven't favorited any yet


# @app.route('/visited_parks')
# def show_favorites():
#     # query the database to find any parks the user has visited, otherwise show message that they haven't visited any yet
