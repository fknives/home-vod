import os,sys
sys.path.append('../')
import context
import unittest
import unittest.mock
import time
from flask import current_app
import backend.data.db as db
from backend.data.data_models import DataError

import backend.data.dao_registration_tokens as sut

class RegistrationTokenDAOTest(unittest.TestCase):

    app = context.create_app(context.default_test_config)

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")
    
    def test_empty_db_contains_no_token(self):
        token = "token"
        
        with self.app.app_context():
            actual = sut.is_valid_token(token)

        self.assertEqual(False, actual)
    
    def test_inserted_token_is_found(self):
        token = "token"
        
        with self.app.app_context():
            sut.insert_token(token)
            actual = sut.is_valid_token(token)

        self.assertEqual(True, actual)

    def test_same_token_cannot_be_inserted_twice(self):
        token = "token"
        
        with self.app.app_context():
            sut.insert_token(token)
            result = sut.insert_token(token)

        self.assertEqual(DataError.REGISTRATION_CODE_ALREADY_EXISTS, result)

    def test_token_deleted_is_not_found(self):
        token = "token"
        
        with self.app.app_context():
            sut.insert_token(token)
            sut.delete_token(token)
            actual = sut.is_valid_token(token)

        self.assertEqual(False, actual)

    def test_tokens_can_be_requested(self):
        expected = ['token-1', 'token-3']
        
        with self.app.app_context():
            sut.insert_token('token-1')
            sut.insert_token('token-2')
            sut.insert_token('token-3')
            sut.delete_token('token-2')
            actual = sut.get_tokens()

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main(verbosity=2)
