from unittest import TestCase
import os

from app import create_app, db
from app.auth.models import User

class BaseTestClass(TestCase):
    def setUp(self):
        # self.app = None # this is only to test dev & testing configs
        self.app = create_app(settings_module="config.testing")
        self.client = self.app.test_client()
        # with self.app.app_context():
        #     db.create_all()

    def tearDown(self):
        with self.app.app_context():
            # to delete all tables from db
            # db.session.remove()
            # db.drop_all()

            # to delete all items from a table
            User.query.delete()
            db.session.commit()
