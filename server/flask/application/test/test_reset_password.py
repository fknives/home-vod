import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_reset_password_tokens
from backend.data import dao_users
from backend.data.data_models import RegisteringUser

class ResetPasswordUnitTest(unittest.TestCase):
 
    url_path = '/reset/password'
    app = create_app(default_test_config)
    client = app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")

    def save_token(self, token, username, expires_at):
        with self.app.app_context():
            dao_reset_password_tokens.insert_token(token=token,username=username,expires_at=expires_at)

    def insert_user(self, user: RegisteringUser):
        with self.app.app_context():
            user_id = dao_users.insert_user(user)
        return user_id

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
    
    def test_without_reset_password_token_error_is_shown(self):
        expected = {'message': 'Invalid Reset Password Token given!','code':461}
        
        data = {'username': 'myname', 'password': 'mypass'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_without_valid_reset_password_token_error_is_shown(self):
        expected = {'message': 'Invalid Reset Password Token given!','code':461}
        
        data = {'username': 'myname', 'password': 'mypass', 'reset_password_token': 'alma'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_without_saved_reset_password_token_error_is_shown(self):
        expected = {'message': 'Invalid Reset Password Token given!','code':461}
        
        data = {'username': 'myname', 'password': 'mypass', 'reset_password_token': 'alma'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_with_expired_reset_password_token_error_is_shown(self, mock_time):
        expected = {'message': 'Invalid Reset Password Token given!','code':461}
        token = 'alma'
        username = 'myname'
        self.save_token(token = token, username = username, expires_at = 10)
        
        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_with_valid_registration_token_but_no_user_error_is_shown(self, mock_time):
        expected = {'message': 'User cannot be found!','code':412}
        token = 'alma'
        username = 'myname'
        self.save_token(token = token, username = username, expires_at = 1100)
        
        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_with_valid_token_and_user_success_is_shown(self, mock_time):
        expected = {'message': 'Password was Saved!','code':201}
        token = 'alma'
        username = 'myname'
        self.save_token(token = token, username = username, expires_at = 1100)
        user = RegisteringUser(
            name = username,
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        
        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_reset_password_can_be_used(self, mock_time):
        expected_keys = {'otp_secret'}
        expected_format = r'^otpauth://totp/FnivesVOD:myname\?secret=[^&]*&issuer=FnivesVOD$'
        token = 'alma'
        username = 'myname'
        self.save_token(token = token, username = username, expires_at = 1100)
        user = RegisteringUser(
            name = username,
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        self.insert_user(user)
        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        self.client.post(self.url_path, data=data)

        login_data = {'username': username, 'password': 'mypass'}
        response = self.client.post('/login', data=login_data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertRegex(actual_response_json['otp_secret'], expected_format)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_same_token_cannot_be_reused(self, mock_time):
        expected = {'message': 'Invalid Reset Password Token given!','code':461}
        token = 'alma'
        username = 'myname'
        self.save_token(token = token, username = username, expires_at = 1100)
        user = RegisteringUser(
            name = username,
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        self.insert_user(user)
        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        self.client.post(self.url_path, data=data)

        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_no_previous_token_can_be_reused_after_reset(self, mock_time):
        expected = {'message': 'Invalid Reset Password Token given!','code':461}
        token = 'alma'
        token2 = 'alma2'
        username = 'myname'
        self.save_token(token = token, username = username, expires_at = 1100)
        self.save_token(token = token2, username = username, expires_at = 1100)
        user = RegisteringUser(
            name = username,
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        self.insert_user(user)
        data = {'username': username, 'password': 'mypass', 'reset_password_token': token}
        self.client.post(self.url_path, data=data)

        data = {'username': username, 'password': 'mypass', 'reset_password_token': token2}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)


if __name__ == '__main__':
    unittest.main(verbosity=2)