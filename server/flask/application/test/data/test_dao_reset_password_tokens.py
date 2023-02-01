import os,sys
sys.path.append('../')
import context
import unittest
import unittest.mock
import time
from flask import current_app
import backend.data.db as db

import backend.data.dao_reset_password_tokens as sut

class ResetPasswordTokenDAOTest(unittest.TestCase):

    app = context.create_app(context.default_test_config)

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_empty_db_contains_no_token(self, mock_time):
        token = "token"
        
        with self.app.app_context():
            actual = sut.is_valid_token(token = token, username = "")

        self.assertEqual(False, actual)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_inserted_token_is_found(self, mock_time):
        token = "token"
        username = "usr"
        
        with self.app.app_context():
            sut.insert_token(token = token, username = username, expires_at = 2000)
            actual = sut.is_valid_token(token = token, username = username)

        self.assertEqual(True, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_inserted_expired_token_is_not_found(self, mock_time):
        token = "token"
        username = "usr"
        
        with self.app.app_context():
            sut.insert_token(token = token, username = username, expires_at = 1000)
            actual = sut.is_valid_token(token = token, username = username)

        self.assertEqual(False, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_token_deleted_is_not_found(self, mock_time):
        token = "token"
        username = "usr"
        
        with self.app.app_context():
            sut.insert_token(token = token, username = username, expires_at = 2000)
            sut.delete_tokens(username = username)
            actual = sut.is_valid_token(token = token, username = username)

        self.assertEqual(False, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_only_given_user_tokens_are_deleted(self, mock_time):
        token = "token"
        username_given = "usr_given"
        username = "usr_other"
        
        with self.app.app_context():
            sut.insert_token(token = token, username = username_given, expires_at = 2000)
            sut.insert_token(token = token, username = username, expires_at = 2000)
            sut.delete_tokens(username = username_given)
            actual = sut.is_valid_token(token = token, username = username)

        self.assertEqual(True, actual)

if __name__ == '__main__':
    unittest.main(verbosity=2)
