import os
import unittest
import unittest.mock
import json
from .context import create_app, default_test_config, create_test_session
from backend.data import db
from backend.data import dao_users
from backend.data import dao_session
from backend.data.data_models import Session
from backend.data.data_models import RegisteringUser

class GetFileMetadataOfUserUnitTest(unittest.TestCase):
 
    url_path = '/file/metadata'
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

    def test_no_headers_returns_unauthorized(self):
        expected = {'message':'Missing Authorization!','code':440}

        response = self.client.get(self.url_path)
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_not_saved_access_token_headers_returns_unauthorized(self):
        expected = {'message':'Invalid Authorization!','code':441}

        response = self.client.get(self.url_path, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    def test_expired_access_token_headers_returns_unauthorized(self):
        session = create_test_session(user_id=2, access_token='token', access_expires_at=1, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':441}
        
        response = self.client.get(self.url_path, headers={'Authorization': 'token'})
        actual_response_json = json.loads(response.data.decode())
        
        self.assertEqual(401, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_sending_non_saved_user_error_is_shown(self, mock_time):
        session = create_test_session(user_id=2, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':442}

        header = {'Authorization': 'token'}
        response = self.client.get(self.url_path, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_authenticated_user_without_parameter_error_is_shown(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message': 'Invalid FileKey (file_key)!', 'code': 416}

        header = {'Authorization': 'token'}
        response = self.client.get(self.url_path, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)


    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_authenticated_user_with_no_data_returns_empty(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {}

        header = {'Authorization': 'token'}
        get_query = {'file_key': 'a'}
        response = self.client.get(self.url_path, headers = header, query_string = get_query)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_one_users_saved_data_other_can_access_it(self, mock_time):
        user_with_metadata = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_with_metadata_id = self.insert_user(user_with_metadata)
        usersession_with_metadata = create_test_session(user_id=user_with_metadata_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(usersession_with_metadata)

        user = RegisteringUser(
            name = 'other',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token2', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'key': 'value'}

        post_header = {'Authorization': 'token'}
        data = json.dumps({'key': 'value'})
        self.client.post(self.url_path, headers = post_header, data = data, content_type='application/json')

        get_header = {'Authorization': 'token2'}
        get_query = {'file_key': 'key'}
        response = self.client.get(self.url_path, headers = get_header, query_string=get_query, content_type='application/json')

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)

if __name__ == '__main__':
    unittest.main(verbosity=2)