#!usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app.config import Config
from app import create_app, db
from models import User, Bot, Task, TaskVersion, BotJob, BotScheduledJob
from util import encode

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI= 'sqlite://'

class BotModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_insert_bot(self):
        u = User(first_name='Anabel',last_name='Almaraz')
        u.set_user_secret('anabelaa85@gmail.com')
        bot = Bot(name = 'botica-test', description = 'prueba', user = u)
        bot.set_bot_secret('botica-test')
        self.assertTrue(bot.user_id == u.id)
        self.assertTrue(bot.is_active == None)

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

    def test_password_hashing(self):
        u = User(first_name='JJLC',last_name='Luna')
        u.set_password('Welcome1')
        self.assertFalse(u.check_password('welcome1'))
        self.assertTrue(u.check_password('Welcome1'))

    def test_user_secret_hashing(self):
        u = User(first_name='JJLC',last_name='Luna')
        u.set_user_secret('javier.luna@i-condor.com')
        self.assertFalse(u.user_secret == encode('javier.Luna@gmail.com'))
        self.assertTrue(u.user_secret == encode('javier.luna@i-condor.com'))

class schedulerCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_createMinuteQueue(self):
        botSch = BotScheduledJob(bot_id = 1, task_id=1, when = "MINUTE;1")
        db.session.add(botSch)
        botSch.enqueue()
        db.session.commit()
        

if __name__ == '__main__':
    unittest.main(verbosity=2)