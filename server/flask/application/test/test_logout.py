import os
import unittest
import unittest.mock
from .context import create_app, default_test_config
from backend.data import db
from backend.data import dao_users
from backend.data import dao_session
from backend.data.data_models import Session
from backend.data.data_models import RegisteringUser

class LogoutUnitTest(unittest.TestCase):
 
    url_path = '/logout'
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

    def assertSession(self, access_token, user_id):
        with self.app.app_context():
             actual_user_id = dao_session.get_user_for_token(access_token)
        self.assertEqual(actual_user_id, user_id)

    def test_no_headers_returns_ok(self):
        expected = ''
        response = self.client.post(self.url_path)
        actual_response = response.data.decode()

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response)

    def test_given_invalid_session_returns_ok(self):
        expected = ''
        response = self.client.post(self.url_path, headers={'Authorization': 'invalid_token'})
        actual_response = response.data.decode()

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_valid_session_returns_and_session_is_invalidated_ok(self, mock_time):
        session = Session(
            user_id=2,
            access_token='access',
            refresh_token='refresh',
            access_expires_at=1010,
            refresh_expires_at=1020
        )
        self.insert_session(session = session)
        self.assertSession(access_token = 'access', user_id = 2)
        expected = ''
        response = self.client.post(self.url_path, headers={'Authorization': 'access'})
        actual_response = response.data.decode()

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response)
        self.assertSession(access_token = 'access', user_id = None)

if __name__ == '__main__':
    unittest.main(verbosity=2)