import os
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest
from webapp import create_app, db
from config import Config
from webapp.main.models import User, Post

class TestConfig(Config):
    TESTING = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # self.assertFalse()
    # self.assertEqual()
    # self.assertTrue()

    def test_user_password(self):
        u = User(username='alex', email='alex@at.com')
        password = 'inteligent'
        u.set_password(password)
        self.assertTrue(u.check_password(password))
        self.assertFalse(u.check_password(password+'a'))

    def test_followers(self):
        users = [
            User(username='Donald', email='Donals@google.com'),
            User(username='Elastyna', email='elxxxx@eyass.net'),
            User(username='AHolland', email='slabefilmy@oj.pl')
        ]

        for u in users:
            db.session.add(u)
        db.session.commit()

        for u in users:
            following = db.session.scalars(u.following.select()).all()
            followers = db.session.scalars(u.followers.select()).all()
            self.assertEqual(following, [])
            self.assertEqual(followers, [])
        
        users[0].follow(users[1]) # Donald follows Elastyna
        users[1].follow(users[0]) # Elastyna follows Donald
        users[1].follow(users[2]) # Elastyna follows AHolland
        # AHolland don't follow anyone
        db.session.commit()

        self.assertTrue(users[0].is_following(users[1]))
        self.assertFalse(users[0].is_following(users[0]))
        self.assertFalse(users[0].is_following(users[2]))
        self.assertTrue(users[1].is_following(users[0]))
        self.assertTrue(users[1].is_following(users[2]))
        self.assertFalse(users[2].is_following(users[0]))

        u2_followers = db.session.scalars(users[2].followers.select()).all()
        self.assertFalse('AHolland' in [x.username for x in u2_followers])
        self.assertTrue('Elastyna' in [x.username for x in u2_followers])
        
        self.assertEqual(users[1].following_counter(), 2)

        users[1].unfollow(users[0]) # Elastyna stops following Donald
        db.session.commit()

        u0_followers = db.session.scalars(users[0].followers.select()).all()
        self.assertFalse('Elastyna' in [x.username for x in u0_followers])

        u1_following = db.session.scalars(users[1].following.select()).all()
        self.assertFalse('Donald' in [x.username for x in u1_following])
        self.assertTrue('AHolland' in [x.username for x in u1_following])

        self.assertEqual(users[0].followers_counter(), 0)
        self.assertEqual(users[2].followers_counter(), 1)
    

    def test_follow_posts(self):
        users = [
            User(username='Donald', email='Donals@google.com'),
            User(username='Elastyna', email='elxxxx@eyass.net'),
            User(username='AHolland', email='slabefilmy@oj.pl'),
            User(username='Jack', email='jackal@jackal.org')
        ]
        db.session.add_all(users)

        posts = [
            Post(title='siemmaaa', body='jo jo yo!', author=users[0]),
            Post(title='my firs', body='it was a long time ago', author=users[0]),
            Post(title='yesterday...', body='all my troubles seemed so far away', author=users[1]),
            Post(title='take it easy', body='baby don\'t worry', author=users[2]),
            Post(title='mama gay', body='wtf?', author=users[3])
        ]
        
        for post in posts:
            db.session.add(post)
        
        db.session.commit()

        users[0].follow(users[1]) # Donald follows Elastyna
        users[1].follow(users[0]) # Elastyna follows Donald
        users[1].follow(users[0]) # duplicate
        users[2].follow(users[1]) # AHolland follows Elastyna
        users[1].follow(users[2]) # Elastyna follows AHolland
        users[2].follow(users[3]) # AHolland follows Jack
        db.session.commit()

        # Donald follows Elastyna
        self.assertEqual(users[0].get_my_and_followers_posts(), [posts[2], posts[1], posts[0]])
        # Elastyna follows Donald and AHolland
        self.assertEqual(users[1].get_my_and_followers_posts(), [posts[3], posts[2], posts[1], posts[0]])
        # AHolland follows Elastyna and Jack
        self.assertEqual(users[2].get_my_and_followers_posts(), [posts[4], posts[3], posts[2]])
        # Jack follows nobody
        self.assertEqual(users[3].get_my_and_followers_posts(), [posts[4]])


if __name__ == '__main__':
    unittest.main(verbosity=2)

