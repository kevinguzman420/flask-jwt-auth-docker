import pytest, json, time
from flask import current_app
from app.auth.models import User, BlacklistToken
from app.db import db
from . import BaseTestClass

# consts
user_email = 'guzmankevin420@gmail.com'

# helper to register an user
def auth_register(self, email, password):
    return self.client.post(
                "/auth/register/",
                data=json.dumps(dict(
                    email=email,
                    password=password
                )),
                content_type="application/json"
            )

def auth_login(self, email, password):
    return self.client.post(
                '/auth/login/',
                data=json.dumps(dict(
                    email=email,
                    password=password
                )),
                content_type='application/json'
            )

class TestAuth(BaseTestClass):

    def test_registration(self):
        """Test for user registration"""
        with self.client:
            resp = auth_register(self, user_email, "123456")
            data = json.loads(resp.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Successfully registered.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(resp.content_type == "application/json")
            self.assertEqual(resp.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        with self.app.app_context():
            user = User(
                email=user_email,
                password='test'
            )
            user.save()
            with self.client:
                resp = auth_register(self, user_email, "123456")
                data = json.loads(resp.data.decode())
                self.assertTrue(data["status"] == 'fail')
                self.assertTrue(
                    data['message'] == "User already exists. Please Log in."
                )
                self.assertTrue(resp.content_type == 'application/json')
                self.assertEqual(resp.status_code, 202)

    def test_registered_user_login(self):
        """ Test for login of registered-user login """
        with self.client:
            # user registration
            resp = auth_register(self, user_email, "123456")
            data_register = json.loads(resp.data.decode())
            self.assertTrue(data_register["status"] == "success")
            self.assertTrue(resp.content_type == 'application/json')
            self.assertEqual(resp.status_code, 201)
            # registered user login
            response = auth_login(self, user_email, "123456")
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data["message"] == "Successfully logged in.")
            self.assertTrue(response.content_type == 'application/json')
            self.assertTrue(response.status_code, 200)

    def test_non_registered_user_login(self):
        """ Test for login of non-registered user """
        with self.client:
            resp = auth_login(self, user_email, "123456")
            data = json.loads(resp.data.decode())
            self.assertTrue(data["status"] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(resp.content_type == 'application/json')
            self.assertEqual(resp.status_code, 404)

    def test_user_status(self):
        """ Test for user status """
        with self.client:
            resp_register = auth_register(self, user_email, "123456")
            response = self.client.get(
                '/auth/status/',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['email'] == user_email)
            self.assertTrue(data['data']['admin'] == 'true' or 'false')
            self.assertEqual(response.status_code, 200)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        with self.client:
            # User registration
            resp_register = auth_register(self, user_email, "123456")
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = auth_login(self, user_email, "123456")
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # valid token logout
            response = self.client.post(
                '/auth/logout/',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout(self):
        """ Testing logout after the token exprires """
        with self.client:
            # user registration
            resp_register = auth_register(self, user_email, "123456")
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = auth_login(self, user_email, "123456")
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == "success")
            self.assertTrue(data_login['message'] == "Successfully logged in.")
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # invalid token logout
            time.sleep(6)
            response = self.client.post(
                '/auth/logout/',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.'
            )
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout after a valid token gets blacklisted """
        with self.client:
            # user registration
            resp_register = auth_register(self, user_email, "123456")
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = auth_login(self, user_email, "123456")
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_login.data.decode())['auth_token'])
            blacklist_token.save()
            # blacklisted valid token logout
            response = self.client.post(
                '/auth/logout/',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_user(self):
        """ Test for user status with a blacklisted valid token """
        with self.client:
            resp_register = auth_register(self, user_email, "123456")
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_register.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            response = self.client.get(
                '/auth/status',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_status_malformed_bearer_token(self):
        """ Test for user status with malformed bearer token """
        with self.client:
            resp_register = auth_register(self, 'joe@gmail.com', '123456')
            response = self.client.get(
                '/auth/status/',
                headers=dict(
                    Authorization='Bearer' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)