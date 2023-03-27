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

class AddFileMetadataUnitTest(unittest.TestCase):
 
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

    def test_expired_access_token_headers_returns_unauthorized(self):
        session = create_test_session(user_id=2, access_token='token', access_expires_at=1, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Invalid Authorization!','code':441}
        
        response = self.client.post(self.url_path, headers={'Authorization': 'token'})
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
    def test_given_authenticated_user_sending_data_shows_success(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'File MetaData Saved!','code':203}

        header = {'Authorization': 'token'}
        data = json.dumps({'key': 'value'})
        response = self.client.post(self.url_path, headers = header, data = data, content_type='application/json')

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_authenticated_user_sending_invalid_data_shows_error(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'message':'Couldn\'t save metadata!','code':415}

        header = {'Authorization': 'token'}
        data = ""
        response = self.client.post(self.url_path, headers = header, data = data, content_type='application/json')

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_authenticated_user_sending_data_can_be_read(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected_of_key_query = {'key': 'value'}
        expected_of_key2_query = {'key2':'value2'}

        data = json.dumps({'key': 'value', 'key2': 'value2'})
        header = {'Authorization': 'token'}
        self.client.post(self.url_path, headers = header, data = data, content_type='application/json')
        get_query_key1 = {'file_key': 'key'}
        response_of_key1 = self.client.get(self.url_path, query_string = get_query_key1, headers = header)
        get_query_key2 = {'file_key': 'key2'}
        response_of_key2 = self.client.get(self.url_path, query_string = get_query_key2, headers = header)

        self.assertEqual(200, response_of_key1.status_code)
        actual_response_json = json.loads(response_of_key1.data.decode())
        self.assertEqual(expected_of_key_query, actual_response_json)

        actual_response_json = json.loads(response_of_key2.data.decode())
        self.assertEqual(200, response_of_key2.status_code)
        self.assertEqual(expected_of_key2_query, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_authenticated_user_data_can_be_overwritten_and_extended(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'key': 'value1'}

        header = {'Authorization': 'token'}
        data = json.dumps({'key': 'value', 'key2': 'value2'})
        self.client.post(self.url_path, headers = header, data = data, content_type='application/json')
        data = json.dumps({'key': 'value1', 'key3': 'value3'})
        self.client.post(self.url_path, headers = header, data = data, content_type='application/json')
        get_query = {'file_key': 'key'}
        response = self.client.get(self.url_path, query_string=get_query, headers = header)

        self.assertEqual(200, response.status_code)
        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(expected, actual_response_json)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_given_authenticated_user_invalid_data_is_not_saved(self, mock_time):
        user = RegisteringUser(
            name = 'banan',
            password = 'citrom',
            otp_secret = 'base32secret3232'
        )
        user_id = self.insert_user(user)
        session = create_test_session(user_id=user_id, access_token='token', access_expires_at=1050, refresh_expires_at=2000)
        self.insert_session(session)
        expected = {'key': 'value'}

        header = {'Authorization': 'token'}
        data = json.dumps({'key': 'value', 'key2': 'value2'})
        self.client.post(self.url_path, headers = header, data = data, content_type='application/json')
        invalid_data = json.dumps([{'key': 'value1', 'key3': 'value3'}])
        self.client.post(self.url_path, headers = header, data = invalid_data, content_type='application/json')
        get_query={'file_key':'key'}
        response = self.client.get(self.url_path, query_string = get_query, headers = header)

        actual_response_json = json.loads(response.data.decode())
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, actual_response_json)


if __name__ == '__main__':
    unittest.main(verbosity=2)