import os
import unittest
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_users
from backend.data.data_models import RegisteringUser

class LoginUnitTest(unittest.TestCase):
 
    url_path = '/login'
    app = create_app(default_test_config)
    client = app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")

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
    
    def test_sending_non_saved_user_error_is_shown(self):
        expected = {'message':'User cannot be found!','code':412}

        data = {'username': 'myname', 'password': 'mypass', 'otp': '124'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_sending_non_found_name_by_name_error_is_shown(self):
        password = 'mypass'
        user = RegisteringUser(
            name = "myname",
            password = password,
            otp_secret = "base32secret3232"
        )
        self.insert_user(user)
        expected = {'message':'User cannot be found!','code':412}

        data = {'username': 'myname2', 'password': password, 'otp': '124'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_sending_non_found_user_by_password_error_is_shown(self):
        username = 'myname'
        user = RegisteringUser(
            name = username,
            password = 'pass',
            otp_secret = "base32secret3232"
        )
        self.insert_user(user)
        expected = {'message':'User cannot be found!','code':412}

        data = {'username': username, 'password': 'pass2', 'otp': '124'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_without_otp_verified_then_secret_is_returned(self):
        user = RegisteringUser(
            name = "myname",
            password = "mypass",
            otp_secret = "base32secret3232",
            was_otp_verified = False
        )
        self.insert_user(user)
        expected_keys = {'otp_secret'}
        expected_format = r'^otpauth://totp/FnivesVOD:myname\?secret=[^&]*&issuer=FnivesVOD$'

        data = {'username': 'myname', 'password': 'mypass'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertRegex(actual_response_json['otp_secret'], expected_format)

    def test_with_otp_verified_success_is_returned(self):
        user = RegisteringUser(
            name = "myname",
            password = "mypass",
            otp_secret = "base32secret3232",
            was_otp_verified = True
        )
        self.insert_user(user)
        expected = {'message':'User found!','code':200}
        
        data = {'username': 'myname', 'password': 'mypass'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)

if __name__ == '__main__':
    unittest.main(verbosity=2)