import unittest
from unittest import TestCase
import os

# from flask_migrate import upgrade
from flask_migrate import Migrate

from models import db, User, Park, Favorited_Park

os.environ['DATABASE_URL'] = "postgresql:///parks_test"

from app import app

class TestAddFavorite(TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_TEST")
        app.config['TESTING'] = True
        with app.app_context():
            # upgrade()
            # Migrate(app, db)
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        db.engine.execute("DROP TABLE alembic_version")

    def setUp(self):
        self.app = app.test_client()
        self.uid = 94566
        u = User.signup("testing", "testing@test.com", "password")
        u.id = self.uid
        self.park = Park()
        self.park_unfavorited = Park()
        db.session.add(self.park)
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        for table in reversed(db.metadata.sorted_tables):
            db.engine.execute(table.delete())
        db.session.commit()
        db.session.remove()

    def test_add_favorite(self):
        favorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==self.park.id, Favorited_Park.user_id==self.u.id).first()
        # first method gets first item from an iterable that matches a condition
        self.assertEqual(favorited_park, None)
        # there shouldn't be any favorited parks at this point

        url = f'/parks/{self.park.id}/add_favorite'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        favorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==self.park.id, Favorited_Park.user_id==self.u.id).first()

        self.assertEqual(favorited_park.user_id, self.u.id)

        unfavorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==self.park_unfavorited.id, Favorited_Park.user_id==self.u.id).first()
        self.assertEqual(unfavorited_park, None)

        url_remove =f'/users/<string:parks_id>/remove-favorite'
        response = self.client.post(url_remove)
        self.assertEqual(response.status_code, 302)
        unfavorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==self.park_unfavorited.id, Favorited_Park.user_id==self.u.id).first()

        self.assertEqual(unfavorited_park.user_id, self.u.id)

if __name__ == '__main__':
    unittest.main()
