import os,re
import unittest
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_registration_tokens

class RegistrationUnitTest(unittest.TestCase):
 
    url_path = '/register'
    app = create_app(default_test_config)
    client = app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")

    def save_token(self, token):
        with self.app.app_context():
            dao_registration_tokens.insert_token(token)

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
    
    def test_without_otp_error_is_shown(self):
        expected = {'message':'Invalid Token!','code':430}
        
        data = {'username': 'myname', 'password': 'mypass'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_sending_non_saved_otp_token_then_error_is_shown(self):
        expected = {'message':'Invalid Token!','code':430}
        
        data = {'username': 'myname', 'password': 'mypass', 'otp': '124'}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_sending_saved_token_with_nonexistent_username_then_otp_secret_is_revealed(self):
        token = '124'
        name = 'myname'
        self.save_token(token)
        expected_keys = {'otp_secret'}
        expected_format = r'^otpauth://totp/FnivesVOD:[^?]*\?secret='+re.escape(name)+r'&issuer=FnivesVOD$'
        
        data = {'username': 'myname', 'password': 'mypass', 'otp': token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertRegex(actual_response_json['otp_secret'], expected_format)

    def test_reusing_token_doesnt_work(self):
        token = '124'
        self.save_token(token)
        first_user_data = {'username': 'myname', 'password': 'mypass', 'otp': token}
        self.client.post(self.url_path, data=first_user_data)
        expected = {'message':'Invalid Token!','code':430}

        data = {'username': 'myname2', 'password': 'mypass', 'otp': token}
        response = self.client.post(self.url_path, data=data)
        
        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_sending_saved_otp_token_but_existing_username_then_error_is_shown(self):
        first_user_token = '124'
        second_user_token = '125'
        same_user_name = 'myname'
        self.save_token(first_user_token)
        self.save_token(second_user_token)
        first_user_data = {'username': same_user_name, 'password': 'mypass', 'otp': first_user_token}
        self.client.post(self.url_path, data=first_user_data)
        expected = {'message':'Username is already taken!','code':411}

        data = {'username': same_user_name, 'password': 'mypass', 'otp': second_user_token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_reusing_token_after_existing_user_error_works(self):
        first_user_token = '124'
        second_user_token = '125'
        same_user_name = 'myname'
        different_user_name = 'myname2'
        self.save_token(first_user_token)
        self.save_token(second_user_token)
        first_user_data = {'username': same_user_name, 'password': 'mypass', 'otp': first_user_token}
        self.client.post(self.url_path, data=first_user_data)
        second_user_data = {'username': same_user_name, 'password': 'mypass', 'otp': second_user_token}
        self.client.post(self.url_path, data=second_user_data)
        expected_keys = {'otp_secret'}
        expected_format = r'^otpauth://totp/FnivesVOD:[^?]*\?secret='+re.escape(different_user_name)+r'&issuer=FnivesVOD$'

        data = {'username': different_user_name, 'password': 'mypass', 'otp': second_user_token}
        response = self.client.post(self.url_path, data=data)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertRegex(actual_response_json['otp_secret'], expected_format)


if __name__ == '__main__':
    unittest.main(verbosity=2)