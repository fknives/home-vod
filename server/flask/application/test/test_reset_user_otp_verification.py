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

class ResetUserOTPVerificationTest(unittest.TestCase):
 
    url_path = '/admin/reset_otp_verification'
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

    def inser_registration_token(self, token: str):
        with self.app.app_context():
            dao_registration_tokens.insert_token(token)

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
    def test_sending_correct_authentication_but_no_otp_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'code': 431, 'message': 'Invalid Token!'}

        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_correct_authentication_and_otp_but_not_priviliged_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = False
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'code': 460, 'message': 'Not Authorized!'}

        header = {'Authorization': 'token'}
        data = {'otp': '{}'.format(correct_code)}
        response = self.client.post(self.url_path, headers = header, data = data)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_correct_privilidged_authentication_and_otp_without_usertoreset_shows_error(self, mock_time):
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
        expected = {'code': 413, 'message': 'username_to_reset cannot be empty!'}

        header = {'Authorization': 'token'}
        data = {'otp': '{}'.format(correct_code)}
        response = self.client.post(self.url_path, headers = header, data = data)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_correct_privilidged_authentication_and_otp_but_nonexistent_usertoreset_shows_error(self, mock_time):
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
        expected = {'message':'User cannot be found!','code':412}

        header = {'Authorization': 'token'}
        data = {'username_to_reset': 'alma', 'otp': '{}'.format(correct_code)}
        response = self.client.post(self.url_path, headers = header, data = data)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_correct_data_otp_verification_is_updated(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
        )
        user_id = self.insert_user(user)
        user_to_reset = RegisteringUser(
            name = 'alma',
            password = '',
            otp_secret = '',
            was_otp_verified = True
        )
        self.insert_user(user_to_reset)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'code': 207, 'message': 'OTP Verification Reset!'}

        header = {'Authorization': 'token'}
        data = {'username_to_reset': '{}'.format(user_to_reset.name), 'otp': '{}'.format(correct_code)}
        response = self.client.post(self.url_path, headers = header, data = data)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(expected, actual_response_json)
        self.assertEqual(200, response.status_code)

if __name__ == '__main__':
    unittest.main(verbosity=2)