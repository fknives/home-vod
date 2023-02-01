import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_users
from backend.data import dao_session
from backend.data.data_models import Session
from backend.data.data_models import RegisteringUser

class PasswordChangeUnitTest(unittest.TestCase):
 
    url_path = '/change/password'
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

    def assertHasSession(self, access_token, user_id):
        with self.app.app_context():
            actual = dao_session.get_user_for_token(access_token)
        self.assertEqual(user_id, actual)

    def test_no_headers_returns_unauthorized(self):
        expected = {'message':'Missing Authorization!','code':440}

        response = self.client.post(self.url_path)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_not_saved_access_token_headers_returns_unauthorized(self):
        expected = {'message':'Invalid Authorization!','code':441}

        response = self.client.post(self.url_path, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_access_token_headers_returns_unauthorized(self, mock_time):
        session = Session(
            user_id=2,
            access_token='token',
            refresh_token='',
            access_expires_at=950,
            refresh_expires_at=1050,
        )
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':441}
        
        response = self.client.post(self.url_path, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_non_saved_user_error_is_shown(self, mock_time):
        session = Session(
            user_id=2,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
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
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
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
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        expected = {'message':'Invalid Token!','code':431}

        data = {'otp': 0}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_auth_correct_but_no_password_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Invalid Password!','code':421}
        
        data = {'otp': correct_code}
        response = self.client.post(self.url_path, data = data, headers = {'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_auth_correct_but_no_new_password_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'New Password cannot be empty!','code':422}
        
        data = {'otp': correct_code, 'password':'pass'}
        response = self.client.post(self.url_path, data=data, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_auth_correct_but_invalid_current_password_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Invalid Password!','code':421}
        
        data = {'otp': correct_code, 'password':'pass', 'new_password': 'new_pass'}
        response = self.client.post(self.url_path, data=data, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_valid_password_change_results_in_new_session(self, mock_time):
        user = RegisteringUser(
            name = 'alma',
            password = 'pass',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        expected_keys = {'access_token', 'refresh_token', 'expires_at'}
        
        correct_code = 585501 #for 1000 and base32secret3232
        data = {'password':'pass', 'new_password': 'pass2', 'otp': correct_code}
        response = self.client.post(self.url_path, data=data, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertEqual(actual_response_json['expires_at'], 1000+20000)
        self.assertHasSession(access_token = actual_response_json['access_token'], user_id = user_id)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_after_password_change_old_session_is_invalid(self, mock_time):
        user = RegisteringUser(
            name = 'alma',
            password = 'pass',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        change_pass_data = {'password':'pass', 'new_password': 'pass2', 'otp': correct_code}
        response = self.client.post(self.url_path, data=change_pass_data, headers={'Authorization': 'token'})
        json.loads(response.data.decode())
        expected = {'message':'Invalid Authorization!','code':441}

        data = {'password':'pass2', 'new_password': 'pass3', 'otp': correct_code}
        response = self.client.post(self.url_path, data=data, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_after_password_change_new_session_is_valid(self, mock_time):
        user = RegisteringUser(
            name = 'alma',
            password = 'pass',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = Session(
            user_id=user_id,
            access_token='token',
            refresh_token='',
            access_expires_at=1050,
            refresh_expires_at=2000
        )
        self.insert_session(session)
        correct_code = 585501 #for 1000 and base32secret3232
        change_pass_data = {'password':'pass', 'new_password': 'pass2', 'otp': correct_code}
        response = self.client.post(self.url_path, data=change_pass_data, headers={'Authorization': 'token'})
        session_response = json.loads(response.data.decode())
        expected_keys = {'access_token', 'refresh_token', 'expires_at'}
        
        data = {'password':'pass2', 'new_password': 'pass3', 'otp': correct_code}
        response = self.client.post(self.url_path, data=data, headers={'Authorization': session_response['access_token']})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertEqual(actual_response_json['expires_at'], 1000+20000)
        self.assertHasSession(access_token = actual_response_json['access_token'], user_id = user_id)


if __name__ == '__main__':
    unittest.main(verbosity=2)