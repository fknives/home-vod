import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_users
from backend.data import dao_registration_tokens
from backend.data import dao_session
from backend.data.data_models import RegisteringUser
from backend.data.data_models import Session

class DeleteRegistrationTokenUnitTest(unittest.TestCase):
 
    url_path = '/admin/delete/registration_token'
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

    def insert_registration_token(self, token: str):
        with self.app.app_context():
            dao_registration_tokens.insert_token(token)

    def assertRegistrationTokenIs(self, token: str, is_valid: bool):
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
        session = Session(
            user_id=2,
            access_token='token',
            refresh_token='',
            access_expires_at=950,
            refresh_expires_at=1050,
        )
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':441}
        
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, headers=header)
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
    def test_sending_correct_data_but_not_priviliged_user_shows_error(self, mock_time):
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
        expected = {'message':'Not Authorized!','code':460}

        data = {'otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_priviliged_user_sending_correct_data_token_is_deleted(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232',
            privileged = True
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
        self.insert_registration_token('123456')
        self.insert_registration_token('abcdef')
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'Token deleted!','code':209}

        data = {'registration_token': '123456', 'otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)
        self.assertRegistrationTokenIs(token = '123456', is_valid = False)
        self.assertRegistrationTokenIs(token = 'abcdef', is_valid = True)

if __name__ == '__main__':
    unittest.main(verbosity=2)