import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config, create_test_session
from backend.data import db
from backend.data import dao_users
from backend.data import dao_registration_tokens
from backend.data import dao_session
from backend.data.data_models import RegisteringUser
from backend.data.data_models import Session

class CreateResetPasswordTokenTest(unittest.TestCase):
 
    url_path = '/admin/reset_password_token'
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

    def insert_session(self, session: Session):
        with self.app.app_context():
            dao_session.insert_user_session(session)

    def assertResetPasswordTokenIs(self, token: str, is_valid: bool):
        with self.app.app_context():
            actual = dao_registration_tokens.is_valid_token(token)
        self.assertEqual(is_valid, actual)
    
    def test_no_headers_returns_unauthorized(self):
        expected = {'message':'Missing Authorization!','code':440}

        response = self.client.post(self.url_path)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_not_saved_access_token_headers_returns_unauthorized(self):
        expected = {'message':'Invalid Authorization!','code':441}

        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, headers=header)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_access_token_headers_returns_unauthorized(self, mock_time):
        session = create_test_session(user_id=2, access_token='token', access_expires_at=1, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':441}
        
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, headers=header)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_non_saved_user_error_is_shown(self, mock_time):
        session = create_test_session(user_id=2, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':442}

        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_no_otp_token_then_error_is_shown(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Token!','code':431}

        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_invalid_otp_token_then_error_is_shown(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Token!','code':431}

        data = {'otp': 0}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_correct_data_but_not_priviliged_user_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Not Authorized!','code':460}

        data = {'otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_no_reset_token_returns_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Invalid Reset Password Token given!','code':459}
        
        data = {'otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data = data, headers = header)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_blank_reset_token_returns_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Invalid Reset Password Token given!','code':459}
        
        data = {'reset_password_token':' ','otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data = data, headers = header)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_usernametoreset_not_send_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'username_to_reset cannot be empty!','code':413}
        
        data = {'reset_password_token':'a','otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data = data, headers = header)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_as_authenticated_privilidged_proper_data_then_reset_password_token_is_saved(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Reset Password token Saved!','code':208}
        
        data = {'reset_password_token':'a', 'username_to_reset': 'c','otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data = data, headers = header)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_resetted_password_token_can_be_user_to_change_password(self, mock_time):
        admin = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
        )
        admin_id = self.insert_user(admin)
        session = create_test_session(user_id=admin_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        user = RegisteringUser(
            name = 'alma',
            password = '',
            otp_secret = ''
        )
        self.insert_user(user)
        correct_code = 585501 #for 1000 and base32secret3232
        reset_token = 'a'
        data = {'reset_password_token':reset_token, 'username_to_reset': user.name,'otp': correct_code}
        header = {'Authorization': 'token'}
        self.client.post(self.url_path, data = data, headers = header)
        expected = {'message':'Password was Saved!','code':201}

        reset_passwod_data = {'reset_password_token':reset_token, 'username': user.name,'password': 'a'}
        response = self.client.post('/reset/password', data = reset_passwod_data)
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)

if __name__ == '__main__':
    unittest.main(verbosity=1)