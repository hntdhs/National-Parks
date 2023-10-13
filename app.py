import os, re
import pdb
from unicodedata import name

import urllib.request, json

from flask import Flask, redirect, render_template, flash, url_for, request, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from models import db, connect_db, User, Park, Article, Campground, Favorited_Park, Visited_Park
from forms import NewUserForm, LoginForm, UserEditForm
# from load_parks import save_parks
from dotenv import load_dotenv
load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
# db = SQLAlchemy(app)
migrate = Migrate(app, db)

# from heroku document
uri = os.environ.get('DATABASE_URL', 'postgresql:///parks_db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use develherokuopment local db.
print(uri)
app.config['SQLALCHEMY_DATABASE_URI'] = uri 
# (os.environ.get('DATABASE_URL', 'postgresql:///parks_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
if not os.environ.get('TESTING'):
    toolbar = DebugToolbarExtension(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True

connect_db(app)

API_KEY = os.getenv('NPS_GOV_API_KEY')
WEATHER_KEY = os.getenv("WEATHER_KEY")

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
        return redirect("/parks")

    else:
        return render_template('no_user_home.html')


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
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            )

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
            # login is good for redirect,
            return redirect("/parks")

        flash("Username and/or password are incorrect", 'danger')

    return render_template('/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("you have logged out", 'success')
    return redirect("/login")


@app.route('/parks')
def show_parks():
    # save_parks()
    return render_template('/logged_in_home.html', parks=Park.query.all())


@app.route('/parks/<string:park_id>')
def park_info(park_id):

    park = Park.query.get_or_404(park_id)
    article_ids_in_db = [article.id for article in Article.query.filter()]
    
    if not article_ids_in_db:
        articlesEndpoint = (f"https://developer.nps.gov/api/v1/articles?parkCode={park.code}&limit=10&API_KEY={API_KEY}")
        req = urllib.request.Request(articlesEndpoint)

        # Execute request and parse response
        response = urllib.request.urlopen(req).read()
        data = json.loads(response.decode('utf-8'))
        

        articles_array = []

        for art in data["data"]:
            if art["id"] not in article_ids_in_db:
            # if art["id"] not in article_ids_in_db and len(art["relatedParks"]) == 1:
                article = Article(id=art["id"], url=art["url"], title=art["title"], description=art["listingDescription"], image_url=art["listingImage"]["url"], image_altText=art["listingImage"]["altText"], park_id=park_id)

                articles_array.append(article)
                db.session.add(article)

        db.session.commit()

    # weather_API_town = park.town.replace(" ", "%")
    # weatherEndpoint = (f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{weather_API_town}?unitGroup=us&key={WEATHER_KEY}")
    # weather_req = urllib.request.Request(weatherEndpoint)
    # weather_response = urllib.request.urlopen(weather_req).read()
    # weather_data = json.loads(weather_response.decode('utf-8'))
    # max = weather_data["days"][0]["tempmax"]

    return render_template('/parks/individual_park.html', park=park, articles=Article.query.all())


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
                wheelchair_access=ground["accessibility"]["wheelchairAccess"]
                # image_title=ground["images"]["title"], 
                # image_url=ground["images"]["url"],  
                # image_altText=ground["images"]["altText"]
            )
        
            db.session.add(campground)

    db.session.commit()
    return render_template('/parks/campgrounds.html', park=park, campgrounds=Campground.query.all())


@app.route('/users/favorites', methods=["GET"])
def show_favorites():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
# need to reference the relationship
    #user = User.query.get_or_404(user_id)
    return render_template('users/favorites.html', favorites=g.user.favorited)

@app.route('/parks/<string:park_id>/add_favorite', methods=["GET", "POST"])
def add_favorite(park_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    favorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==park_id, Favorited_Park.user_id==g.user.id).first()

    if not favorited_park:
        favorited = Favorited_Park(parks_id=park_id, user_id=g.user.id)
        db.session.add(favorited)

    flash("Park added to favorites")

    db.session.commit()

    return redirect(f"/parks/{park_id}")


@app.route('/users/<string:parks_id>/remove-favorite', methods=["GET", "POST"])
def unfavorite(parks_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id=g.user.id
    favorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==parks_id, Favorited_Park.user_id==user_id).first()
    db.session.delete(favorited_park)
    #g.user.favorited.remove(favorited_park)
    db.session.commit()

    return redirect(f"/users/favorites")


@app.route('/users/visited', methods=["GET"])
def show_visited():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    return render_template('users/visited.html', visited=g.user.visited)


@app.route('/parks/<string:park_id>/add_visited', methods=["GET", "POST"])
def add_visited(park_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    visited_park = Visited_Park.query.filter(Visited_Park.parks_id==park_id, Visited_Park.user_id==g.user.id).first()

    if not visited_park:
        visited = Visited_Park(parks_id=park_id, user_id=g.user.id)
        db.session.add(visited)

    flash("Park added to your collection of visited parks")

    db.session.commit()

    return redirect(f"/parks/{park_id}")


@app.route('/users/<string:parks_id>/remove-visited', methods=["GET", "POST"])
def unvisit(parks_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user_id=g.user.id
    visited_park = Visited_Park.query.filter(Visited_Park.parks_id==parks_id, Visited_Park.user_id==user_id).first()
    db.session.delete(visited_park)
    #g.user.favorited.remove(favorited_park)
    db.session.commit()

    return redirect(f"/users/visited")
