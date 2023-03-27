import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_users
from backend.data import dao_session
from backend.data.data_models import RegisteringUser

class OTP_VerificationUnitTest(unittest.TestCase):

    url_path = '/otp_verification'
    app = create_app(default_test_config)
    client = app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")

    def insert_user(self, user):
        with self.app.app_context():
            user_id = dao_users.insert_user(user)
        return user_id

    def assertHasSession(self, access_token, user_id):
        with self.app.app_context():
            actual = dao_session.get_user_for_token(access_token)
        self.assertEqual(user_id, actual)

    def assertUserOTPIs(self, user_id, was_otp_verified):
        with self.app.app_context():
            actual = dao_users.get_user_by_id(user_id)
        self.assertEqual(was_otp_verified, actual.was_otp_verified)
    
    def test_without_username_error_is_shown(self):
        expected = {'message':'Username cannot be empty!','code':410}
        
        response = self.client.post(self.url_path)
        
        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_without_password_error_is_shown(self):
        expected = {'message':'Password cannot be empty!','code':420}

        data = {'username': 'myname'}
        response = self.client.post(self.url_path, data=data)
        
        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)
    
    def test_sending_non_saved_user_error_is_shown(self):
        expected = {'message':'User cannot be found!','code':412}

        data = {'username': 'myname', 'password': 'mypass', 'otp': '124'}
        response = self.client.post(self.url_path, data=data)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_sending_non_found_user_by_name_error_is_shown(self):
        password = 'mypass'
        user = RegisteringUser(
            name = "myname",
            password = password,
            otp_secret = "base32secret3232"
        )
        user_id = self.insert_user(user)
        expected = {'message':'User cannot be found!','code':412}

        data = {'username': 'myname2', 'password': password, 'otp': '124'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)
        self.assertUserOTPIs(user_id = user_id, was_otp_verified = False)

    def test_sending_non_found_user_by_password_error_is_shown(self):
        username = 'myname'
        user = RegisteringUser(
            name = username,
            password = 'pass',
            otp_secret = "base32secret3232"
        )
        user_id = self.insert_user(user)
        expected = {'message':'User cannot be found!','code':412}

        data = {'username': username, 'password': 'pass2', 'otp': '124'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)
        self.assertUserOTPIs(user_id = user_id, was_otp_verified = False)

    def test_without_otp_error_is_shown(self):
        user = RegisteringUser(
            name = "myname",
            password = "mypass",
            otp_secret = "base32secret3232"
        )
        user_id = self.insert_user(user)
        expected = {'message':'Invalid Token!','code':431}

        data = {'username': 'myname', 'password': 'mypass'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)
        self.assertUserOTPIs(user_id = user_id, was_otp_verified = False)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_invalid_otp_token_then_error_is_shown(self, mock_time):
        user = RegisteringUser(
            name = "myname",
            password = "mypass",
            otp_secret = "base32secret3232"
        )
        user_id = self.insert_user(user)
        invalid_code = 1
        expected = {'message':'Invalid Token!','code':431}

        data = {'username': 'myname', 'password': 'mypass', 'otp': '{}'.format(invalid_code)}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)
        self.assertUserOTPIs(user_id = user_id, was_otp_verified = False)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_proper_otp_token_then_session_is_returned(self, mock_time):
        user = RegisteringUser(
            name = "myname",
            password = "mypass",
            otp_secret = "base32secret3232"
        )
        user_id = self.insert_user(user)
        correct_code = 585501 #for 1000 and base32secret3232
        expected_keys = {'access_token', 'media_token', 'refresh_token', 'expires_at'}
        
        data = {'username': 'myname', 'password': 'mypass', 'otp': '{}'.format(correct_code)}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertEqual(actual_response_json['expires_at'], 1000+20000)
        self.assertHasSession(access_token = actual_response_json['access_token'], user_id = user_id)
        self.assertUserOTPIs(user_id = user_id, was_otp_verified = True)

if __name__ == '__main__':
    unittest.main(verbosity=2)