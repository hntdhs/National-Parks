import os
import pdb
from unicodedata import name

import urllib.request, json

from flask import Flask, redirect, render_template, flash, url_for, request, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from models import db, connect_db, User, Park, Article, Campground
from models import Favorited_Park
# from models import Visited_Park
from forms import NewUserForm, LoginForm, UserEditForm
# from load_parks import save_parks
from dotenv import load_dotenv
load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
# db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///parks_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

connect_db(app)

API_KEY = os.getenv('NPS_GOV_API_KEY')

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
        # followed parks = [list comprehension], parks wishlist = [list comprehension], pass into the template below
        return render_template('logged_in_home.html')

    else:
        return render_template('no_user_home.html')

# @app.route('/national-parks', methods=["GET"])
# def getNationalParks():
#     """
#         - Hits the external API to get all the parks
#         - Filter the parks to only include National Parks
#         - Return the National Parks
#     """
#     return 'Works!'

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there already is a user with that username: flash message
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

        # db.session.commit()

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
    # pdb.set_trace()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!")
            # return render_template('logged_in_home.html')
            # redirect to url that's logged in homepage and that would have api call
            # login is good for redirect,
            return redirect("/parks")

    flash("Username and/or password are incorrect", 'danger')
        # do i need to add code to make this display? the flash for a successful login doesn't work either

    return render_template('/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    do_logout()

    flash("you have logged out", 'success')
    # the logout doesn't work but the flash message doesn't show up
    return redirect("/login")


@app.route('/parks')
def show_parks():
    # save_parks()
    return render_template('/logged_in_home.html', parks=Park.query.all())
    # after switching over to the parks=Park.query, what is the point of park_array? maybe it's not necessary?


@app.route('/parks/<string:park_id>')
def park_info(park_id):
    # seems to be working, clicked on the link for Biscayne and set_trace gave me bisc for park.code and the full name for park.name

    park = Park.query.get_or_404(park_id)
    # pdb.set_trace()
    articlesEndpoint = (f"https://developer.nps.gov/api/v1/articles?parkCode={park.code}&limit=10&API_KEY={API_KEY}")
    req = urllib.request.Request(articlesEndpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))
    article_ids_in_db = [article.id for article in Article.query.all()]

    articles_array = []

    for art in data["data"]:
        if art["id"] not in article_ids_in_db:
        # if art["id"] not in article_ids_in_db and len(art["relatedParks"]) == 1:
            article = Article(id=art["id"], url=art["url"], title=art["title"], description=art["listingDescription"], image_url=art["listingImage"]["url"], image_altText=art["listingImage"]["altText"])

            articles_array.append(article)
            db.session.add(article)

    db.session.commit()
    return render_template('/parks/individual_park.html', park=park, articles=Article.query.all())
    # is there going to be a problem here that I'm doing an Article.query.all, which would theoretically get every article for every park? should it be Article.query.park_id or whatever?


@app.route('/parks/campgrounds/<string:park_id>')
def show_campgrounds(park_id):

    park = Park.query.get_or_404(park_id)

    campgroundsEndpoint = (f"https://developer.nps.gov/api/v1/campgrounds?parkCode={park.code}&API_KEY={API_KEY}")
    req = urllib.request.Request(campgroundsEndpoint)

    # Execute request and parse response
    response = urllib.request.urlopen(req).read()
    data = json.loads(response.decode('utf-8'))
    campground_ids_in_db = [campground.id for campground in Campground.query.all()]

    for ground in data["data"]:
        if ground["id"] not in campground_ids_in_db:
            campground = Campground(
                id=ground["id"], 
                url=ground["url"], 
                name=ground["name"], 
                description=ground["description"], 
                reservation_info=ground["reservationInfo"], 
                reservation_url=ground["reservationUrl"], 
                wheelchair=ground["accessibility"]["wheelchairAccess"]
                # image_title=ground["images"]["title"], 
                # image_url=ground["images"]["url"],  
                # image_altText=ground["images"]["altText"]
            )
        
            db.session.add(campground)

    db.session.commit()
    return render_template('/parks/campgrounds.html', park=park, campgrounds=Campground.query.all())
    # the url in the browser doesn't have the park id, it's just campgrounds.html, whereas individual park page has the park id. /parks/campgrounds.html not found on server. 
    # look at how the link is being made in logged in home.html


@app.route('/users/<int:user_id>/favorite_parks', methods=["GET"])
def show_favorites(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
# need to reference the relationship
    user = User.query.get_or_404(user_id)
    return render_template('users/favorites.html', user=user, favorites=user.favorited)

@app.route('/parks/<string:park_id>/add_favorite', methods=["GET", "POST"])
def add_favorite(park_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    favorited_park = Favorited_Park.query.filter(park_id)
    # want to see if it's in db and if not add it
    if favorited_park.user_id == g.user.id:
        return abort(403)

    user_favorites = g.user.favorited
    # favorites?

    if favorited_park in user_favorites:
        g.user.favorited = [favorite for favorite in user_favorites if favorite != favorited_park]
    else:
        g.user.favorited.append(favorited_park)

    db.session.commit()

    return redirect("/")
    # but I don't want to redirect them to main page - is there a way to just stay on the page? can i just not return anything?
# in parks folder, though note in warbler the route is /messages/<int:message_id>/like, and there's nothing in the messages folder except new.html and show.html


# @app.route('/visited_parks')
# def show_favorites():
#     # query the database to find any parks the user has visited, otherwise show message that they haven't visited any yet
# render template visited.html
