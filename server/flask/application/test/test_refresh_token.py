import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_session
from backend.data.data_models import RegisteringUser
from backend.data.data_models import Session

class RefreshTokenUnitTest(unittest.TestCase):

    url_path = '/refresh/token'
    app = create_app(default_test_config)
    client = app.test_client()

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")

    def insert_session(self, session: Session):
        with self.app.app_context():
            dao_session.insert_user_session(session)

    def assertHasSession(self, access_token, user_id):
        with self.app.app_context():
            actual = dao_session.get_user_for_token(access_token)
        self.assertEqual(user_id, actual)
    
    def test_no_refresh_token_returns_error(self):
        expected = {'message':'Invalid Refresh Token!','code':450}

        response = self.client.post(self.url_path)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_not_saved_refresh_token_returns_error(self):
        expected = {'message':'Invalid Refresh Token!','code':450}

        response = self.client.post(self.url_path, data={'refresh_token': 'token'})
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_if_token_is_exists_2_times_then_invalid(self, mock_time):
        session1 = Session(
            user_id = 1,
            access_token = "a",
            refresh_token = "token",
            access_expires_at = 5000,
            refresh_expires_at = 5000,
        )
        session2 = Session(
            user_id = 2,
            access_token = "b",
            refresh_token = "token",
            access_expires_at = 6000,
            refresh_expires_at = 6000,
        )
        self.insert_session(session1)
        self.insert_session(session2)
        expected = {'message':'Invalid Refresh Token!','code':450}
        
        response = self.client.post(self.url_path, data={'refresh_token': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_refresh_token_then_invalid(self, mock_time):
        session = Session(
            user_id = 1,
            access_token = "a",
            refresh_token = "token",
            access_expires_at = 6000,
            refresh_expires_at = 900,
        )
        self.insert_session(session)
        expected = {'message':'Invalid Refresh Token!','code':450}
        
        response = self.client.post(self.url_path, data={'refresh_token': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_access_token_but_non_expires_refresh_token_then_new_is_returned(self, mock_time):
        session = Session(
            user_id = 1,
            access_token = "a",
            refresh_token = "token",
            access_expires_at = 900,
            refresh_expires_at = 6000,
        )
        self.insert_session(session)
        expected_keys = {'access_token', 'refresh_token', 'expires_at'}
        
        response = self.client.post(self.url_path, data={'refresh_token': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_keys, set(actual_response_json.keys()))
        self.assertEqual(actual_response_json['expires_at'], 1000+20000)
        self.assertHasSession(access_token = actual_response_json['access_token'], user_id = 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)