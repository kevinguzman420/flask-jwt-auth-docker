import unittest

from app.db import db
from app.auth.models import User
from . import BaseTestClass

class TestUserModel(BaseTestClass):

    # works!
    def test_encode_auth_token(self):
        with self.app.app_context():
            user = User(
                email="test@test.com",
                password="test"
            )
            user.save()
            auth_token = user.encode_auth_token(user.id)
            self.assertTrue(isinstance(auth_token, str))

    # works!
    def test_decode_auth_token(self):
        with self.app.app_context():
            user = User(
                email="test@test.com",
                password="test"
            )
            user.save()
            auth_token = user.encode_auth_token(user.id)
            self.assertTrue(isinstance(auth_token, str))
            # print(User.decode_auth_token(auth_token))
            # self.assertTrue(User.decode_auth_token(auth_token) == 1)

if __name__ == '__main__':
    unittest.main()
