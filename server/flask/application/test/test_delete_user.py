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

class DeleteTokenUnitTest(unittest.TestCase):
 
    url_path = '/admin/delete/user'
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

    def assert_user(self, user_id: str, exists: bool):
        with self.app.app_context():
            actual = dao_users.get_user_by_id(user_id)
        self.assertEqual(exists, actual is not None)

    def assert_session(self, access_token: str, exists: bool):
        with self.app.app_context():
            actual = dao_session.get_user_for_token(access_token)
        self.assertEqual(exists, actual is not None)
    
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

        data = {'username_to_delete': 'guest-2', 'otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_priviliged_user_sending_correct_data_user_is_deleted(self, mock_time):
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
        guest1_user_id=self.insert_user(RegisteringUser(name = 'guest-1',password = '123',otp_secret = '',))
        guest2_user_id=self.insert_user(RegisteringUser(name = 'guest-2',password = '123',otp_secret = '',))
        guest1_session = Session(
            user_id=guest1_user_id,
            access_token='a-1',
            refresh_token='r-1',
            access_expires_at=2000,
            refresh_expires_at=3000
        )
        guest2_session = Session(
            user_id=guest2_user_id,
            access_token='a-2',
            refresh_token='r-2',
            access_expires_at=2000,
            refresh_expires_at=3000
        )
        self.insert_session(guest1_session)
        self.insert_session(guest2_session)
        correct_code = 585501 #for 1000 and base32secret3232
        expected = {'message':'User deleted!','code':206}

        data = {'username_to_delete': 'guest-2', 'otp': correct_code}
        header = {'Authorization': 'token'}
        response = self.client.post(self.url_path, data=data, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)
        self.assert_user(user_id = guest1_user_id, exists = True)
        self.assert_user(user_id = guest2_user_id, exists = False)
        self.assert_session(access_token = 'a-1', exists = True)
        self.assert_session(access_token = 'a-2', exists = False)
        

if __name__ == '__main__':
    unittest.main(verbosity=2)