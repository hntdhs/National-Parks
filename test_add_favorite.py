import unittest
from unittest import TestCase
import os

# from flask_migrate import upgrade
from flask_migrate import Migrate, upgrade

from models import db, User, Park, Favorited_Park

os.environ['DATABASE_URL_TEST'] = "postgresql:///parks_test"
os.environ['TESTING'] = 'True'
from app import app

class TestAddFavorite(TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_TEST")
        app.config['TESTING'] = True
        print(app.config['SQLALCHEMY_DATABASE_URI'])
        with app.app_context():
            upgrade()
            Migrate(app, db)
            #db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        db.engine.execute("DROP TABLE alembic_version")

    def setUp(self):
        
        if not getattr(self, 'u', None):
            self.uid = 94566
            u = User.signup("testing", "testing@test.com", "password")
            u.id = self.uid
            park_data = {
                'name': 'Park1',
                'code': 'park1',
                'description': 'great park',
                'ent_fees_cost': 1,
                'state': 'MN',
                'hours': '8-10',
                'town': 'NoWhere',

            }
            self.park = Park(
                id='test-park-1',
                **park_data
                )
            self.park_unfavorited = Park(
                id='test-park-2',
                **park_data
                )
            db.session.add(u)
            db.session.add(self.park)
            db.session.commit()
            db.session.expunge(u)
            db.session.expunge(self.park)

        self.client = app.test_client()
        with self.client.session_transaction() as sess:
            sess['curr_user'] = u.id

        self.u = User.query.get(self.uid)

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

    def test_remove_favorite(self):
        favorited_park = Favorited_Park(parks_id=self.park.id, user_id=self.u.id)
        db.session.add(favorited_park)        

        url_remove =f'/users/{self.park.id}/remove-favorite'
        response = self.client.post(url_remove)
        self.assertEqual(response.status_code, 302)
        unfavorited_park = Favorited_Park.query.filter(Favorited_Park.parks_id==self.park_unfavorited.id, Favorited_Park.user_id==self.u.id).first()

        self.assertEqual(unfavorited_park, None)

if __name__ == '__main__':
    unittest.main()
