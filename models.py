from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

bcrypt = Bcrypt()
db = SQLAlchemy()


user_visited = db.table(
    'user_visited',
    db.Column('user_id', db.Integer, db.ForeighKey('user_id')),
    db.Column('park_id', db.Integer, db.ForeignKey('park_id'))
)

user_favorited = db.table(
    'user_favorited',
    db.Column('user_id', db.Integer, db.ForeighKey('user_id')),
    db.Column('park_id', db.Integer, db.ForeignKey('park_id'))
)
# the video I watched didn't have these as classes, but in Warbler they are

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    location = db.Column(
        db.Text,
        nullable=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    user_favorites = db.relationship(
        "User",
        secondary="favorites",
        primaryjoin=(Favorite.user_id == id),
        secondaryjoin=(Favorite.park_id == id)
    )


    # parks = relationship('Park')

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Park(db.Model):

    __tablename__ = 'parks'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    code = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    ent_fees_cost = db.Column(
        db.Text,
        nullable=False,
    )

    ent_fees_description = db.Column(
        db.Text,
        nullable=False,
    )

    ent_fees_title = db.Column(
        db.Text,
        nullable=False,
    )

    ent_passes_cost = db.Column(
        db.Text,
        nullable=True,
    )

    ent_passes_description = db.Column(
        db.Text,
        nullable=True,
    )

    ent_passes_title = db.Column(
        db.Text,
        nullable=True,
    )

    activity = db.Column(
        db.Text,
        nullable=True,
    )

    state = db.Column(
        db.Text,
        nullable=False,
    )

    phone = db.Column(
        db.Text,
        nullable=True,
    )

    directions_url = db.Column(
        db.Text,
        nullable=True,
    )

    hours = db.Column(
        db.Text,
        nullable=False,
    )

    town = db.Column(
        db.Text,
        nullable=False,
    )

    image_title = db.Column(
        db.Text,
        nullable=False,
    )

    image_altText = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
    )

    fees = db.Column(
        db.Float,
        # is Float right? could  do string just so I dontv lose formatting wiuth dollar signs
        nullable=False,
    )

    articles = db.relationship(
        "Article", backref=db.backref("user")
    )

    # users = relationship('User')

class Article(db.Model):

    __tablename__ = 'articles'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    url = db.Column(
        db.Text,
    )

    title = db.Column(
        db.Text,
    )

    description = db.Column(
        db.Text,
    )

    image_url = db.Column(
        db.Text,
    )

    image_altText = db.Column(
        db.Text,
    )

class Campground(db.Model):

    __tablename__ = 'campgrounds'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    url = db.Column(
        db.Text,
    )

    name = db.Column(
        db.Text
    )

    description = db.Column(
        db.Text
    )

    audio_description = db.Column(
        db.Text
    )

    reservation_info = db.Column(
        db.Text
    )

    reservation_url = db.Column(
        db.Text
    )
    
    image_title = db.Column(
        db.Text
    )
    # ************* each iteration of Campground has 1 name, 1 url, 1 description, etc. But they have multiple images. Does it matter that there's only one column for image url if there's multiple images?

    image_url = db.Column(
        db.Text
    )

    image_altText = db.Column(
        db.Text,
    )


# see around line 99 in warbler for adding relationships
class Favorite(db.Model):

    __tablename__ = 'favorites'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    parks_id = db.Column(
        db.Integer,
        db.ForeignKey('parks.id', ondelete='CASCADE'),
        nullable=False,
    ) 



# class Visited_Park(db.Model):

#     __tablename__ = 'visited'

#     user_id = db.Column(
#         db.Integer,
#         db.ForeignKey('users.id', ondelete='CASCADE'),
#         nullable=False,
#     )

#     parks_id = db.Column(
#         db.Integer,
#         db.ForeignKey('parks.id', ondelete='CASCADE'),
#         nullable=False,
#     ) 






def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)