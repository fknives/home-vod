import os,sys
sys.path.append('../')
import context
import unittest
import unittest.mock
import time
from flask import current_app
from backend.data import db
from backend.data.data_models import Session

import backend.data.dao_session as sut

# Notes to myself:
# test nees tu start with test
# sys.path.append('../') appends the path so context can be imported
# with self.app.app_context(): is required to have current_app, if no request is running

class SessionDAOTest(unittest.TestCase):

    app = context.create_app(context.default_test_config)

    def setUp(self):
        with self.app.app_context():
            db.init_db()

    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")

    def test_empty_db_contains_no_token(self):
        expected = None
        token = "token"
        
        with self.app.app_context():
            actual = sut.get_user_for_token(token)

        self.assertEqual(expected, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_inserted_token_is_found(self, mock_time):
        assert time.time() == 1000
        expected = 13
        token = "token"
        session = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )

        with self.app.app_context():
            sut.insert_user_session(session)
            actual = sut.get_user_for_token(token)

        self.assertEqual(expected, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_same_token_results_in_not_found(self, mock_time):
        assert time.time() == 1000
        expected = None
        token = "token"
        session1 = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        session2 = Session(
            user_id = 14,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session1)
            sut.insert_user_session(session2)
            actual = sut.get_user_for_token(token)

        self.assertEqual(expected, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_access_token_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        token = "token"
        session = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 500,
            refresh_expires_at = 2000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session)
            actual = sut.get_user_for_token(token)

        self.assertEqual(expected, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_refresh_token_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        token = "token"
        session = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 2500,
            refresh_expires_at = 500
        )
        
        with self.app.app_context():
            sut.insert_user_session(session)
            actual = sut.get_user_for_token(token)

        self.assertEqual(expected, actual)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_deleted_session_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        token = "token"
        session = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session = session)
            sut.delete_user_session(access_token = token)
            actual = sut.get_user_for_token(access_token = token)

        self.assertEqual(expected, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_deleted_all_user_session_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        session1 = Session(
            user_id = 13,
            access_token = "token1",
            refresh_token = "refresh_token1",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        session2 = Session(
            user_id = 13,
            access_token = "token2",
            refresh_token = "refresh_token2",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        session_of_different_user = Session(
            user_id = 14,
            access_token = "token3",
            refresh_token = "refresh_token3",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session = session1)
            sut.insert_user_session(session = session2)
            sut.insert_user_session(session = session_of_different_user)
            sut.delete_all_user_session_by_user_id(user_id=13)
            actual1 = sut.get_user_for_token(access_token = session1.access_token)
            actual2 = sut.get_user_for_token(access_token = session2.access_token)
            actual_of_different_user = sut.get_user_for_token(access_token = session_of_different_user.access_token)

        self.assertEqual(expected, actual1)
        self.assertEqual(expected, actual2)
        self.assertEqual(session_of_different_user.user_id, actual_of_different_user)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_after_new_single_session_old_session_is_not_returned(self, mock_time):
        assert time.time() == 1000
        token = "token"
        new_token = "new_token"
        session = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        new_session = session = Session(
            user_id = 13,
            access_token = new_token,
            refresh_token = "refresh_token",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        expected_old = None
        expected_new = 13
        
        with self.app.app_context():
            sut.insert_user_session(session = session)
            sut.create_new_single_session(session = new_session)
            actual_old = sut.get_user_for_token(access_token = token)
            actual_new = sut.get_user_for_token(access_token = new_token)

        self.assertEqual(expected_old, actual_old)
        self.assertEqual(expected_new, actual_new)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_after_swap_refresh_session_old_session_is_not_returned(self, mock_time):
        assert time.time() == 1000
        token = "token"
        new_token = "new_token"
        session = Session(
            user_id = 13,
            access_token = token,
            refresh_token = "refresh_token",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        new_session = session = Session(
            user_id = 13,
            access_token = new_token,
            refresh_token = "refresh_token2",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        expected_old = None
        expected_new = 13
        
        with self.app.app_context():
            sut.insert_user_session(session = session)
            sut.swap_refresh_session(refresh_token = session.refresh_token, session = new_session)
            actual_old = sut.get_user_for_token(access_token = token)
            actual_new = sut.get_user_for_token(access_token = new_token)

        self.assertEqual(expected_old, actual_old)
        self.assertEqual(expected_new, actual_new)


if __name__ == '__main__':
    unittest.main(verbosity=2)
