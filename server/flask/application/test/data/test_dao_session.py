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

    def test_empty_db_contains_no_session(self):
        expected = None
        
        with self.app.app_context():
            actual_by_access = sut.get_user_for_token('access')
            actual_by_media = sut.get_user_for_media_token('media')
            actual_by_refresh = sut.get_user_for_token('refresh')

        self.assertEqual(expected, actual_by_access)
        self.assertEqual(expected, actual_by_media)
        self.assertEqual(expected, actual_by_refresh)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_inserted_token_is_found(self, mock_time):
        assert time.time() == 1000
        expected = 13
        access_token = "access"
        refresh_token = "refresh"
        media_token = "media"
        session = Session(
            user_id = 13,
            access_token = access_token,
            media_token = media_token,
            refresh_token = refresh_token,
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )

        with self.app.app_context():
            sut.insert_user_session(session)
            actual_by_access = sut.get_user_for_token(access_token)
            actual_by_media = sut.get_user_for_media_token(media_token)
            actual_by_refresh = sut.get_user_for_refresh_token(refresh_token)

        self.assertEqual(expected, actual_by_access)
        self.assertEqual(expected, actual_by_media)
        self.assertEqual(expected, actual_by_refresh)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_same_access_token_results_in_not_found(self, mock_time):
        assert time.time() == 1000
        expected = None
        access_token = "token"
        session1 = Session(
            user_id = 13,
            access_token = access_token,
            media_token = "media_token_1",
            refresh_token = "refresh_token_1",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        session2 = Session(
            user_id = 14,
            access_token = access_token,
            media_token = "media_token_2",
            refresh_token = "refresh_token_2",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session1)
            sut.insert_user_session(session2)
            actual = sut.get_user_for_token(access_token)

        self.assertEqual(expected, actual)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_same_access_media_token_results_in_not_found(self, mock_time):
        assert time.time() == 1000
        expected = None
        media_token = "token"
        session1 = Session(
            user_id = 13,
            access_token = "access_1",
            media_token = media_token,
            refresh_token = "refresh_token1",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        session2 = Session(
            user_id = 14,
            access_token = "access_2",
            media_token = media_token,
            refresh_token = "refresh_token2",
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session1)
            sut.insert_user_session(session2)
            actual = sut.get_user_for_media_token(media_token)

        self.assertEqual(expected, actual)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_same_access_refresh_token_results_in_not_found(self, mock_time):
        assert time.time() == 1000
        expected = None
        refresh_token = "token"
        session1 = Session(
            user_id = 13,
            access_token = "access1",
            media_token = "media1",
            refresh_token = refresh_token,
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        session2 = Session(
            user_id = 14,
            access_token = "access2",
            media_token = "media2",
            refresh_token = refresh_token,
            access_expires_at = 2000,
            refresh_expires_at = 4000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session1)
            sut.insert_user_session(session2)
            actual = sut.get_user_for_refresh_token(refresh_token)

        self.assertEqual(expected, actual)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_access_token_isnt_returned_but_refresh_is(self, mock_time):
        assert time.time() == 1000
        expected = None
        access_token = "access"
        media_token = "media"
        refresh_token = "refresh"
        expected_refresh_user_id = 13
        session = Session(
            user_id = 13,
            access_token = access_token,
            media_token = media_token,
            refresh_token = refresh_token,
            access_expires_at = 500,
            refresh_expires_at = 2000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session)
            actual_by_access = sut.get_user_for_token(access_token)
            actual_by_media = sut.get_user_for_media_token(media_token)
            actual_by_refresh = sut.get_user_for_refresh_token(refresh_token)

        self.assertEqual(expected, actual_by_access)
        self.assertEqual(expected, actual_by_media)
        self.assertEqual(expected_refresh_user_id, actual_by_refresh) # but by refresh it is

    @unittest.mock.patch('time.time', return_value=1000)
    def test_expired_refresh_token_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        access_token = "access"
        media_token = "media"
        refresh_token = "refresh"
        session = Session(
            user_id = 13,
            access_token = access_token,
            media_token = media_token,
            refresh_token = refresh_token,
            access_expires_at = 2500,
            refresh_expires_at = 500
        )
        
        with self.app.app_context():
            sut.insert_user_session(session)
            actual_by_access = sut.get_user_for_token(access_token)
            actual_by_media = sut.get_user_for_media_token(media_token)
            actual_by_refresh = sut.get_user_for_refresh_token(refresh_token)

        self.assertEqual(expected, actual_by_access)
        self.assertEqual(expected, actual_by_media)
        self.assertEqual(expected, actual_by_refresh)
    
    @unittest.mock.patch('time.time', return_value=1000)
    def test_deleted_session_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        access_token = "access"
        media_token = "media"
        refresh_token = "refresh"
        session = Session(
            user_id = 13,
            access_token = access_token,
            media_token = media_token,
            refresh_token = refresh_token,
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session = session)
            sut.delete_user_session(access_token = access_token)
            actual_by_access = sut.get_user_for_token(access_token)
            actual_by_media = sut.get_user_for_media_token(media_token)
            actual_by_refresh = sut.get_user_for_refresh_token(refresh_token)

        self.assertEqual(expected, actual_by_access)
        self.assertEqual(expected, actual_by_media)
        self.assertEqual(expected, actual_by_refresh)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_deleted_all_user_session_isnt_returned(self, mock_time):
        assert time.time() == 1000
        expected = None
        session1 = Session(
            user_id = 13,
            access_token = "token1",
            media_token = "media_token1",
            refresh_token = "refresh_token1",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        session2 = Session(
            user_id = 13,
            access_token = "token2",
            media_token = "media_token2",
            refresh_token = "refresh_token2",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        session_of_different_user = Session(
            user_id = 14,
            access_token = "token3",
            media_token = "media_token3",
            refresh_token = "refresh_token3",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        
        with self.app.app_context():
            sut.insert_user_session(session = session1)
            sut.insert_user_session(session = session2)
            sut.insert_user_session(session = session_of_different_user)
            sut.delete_all_user_session_by_user_id(user_id=13)
            actual1_by_access = sut.get_user_for_token(access_token = session1.access_token)
            actual2_by_access = sut.get_user_for_token(access_token = session2.access_token)
            actual1_by_media = sut.get_user_for_media_token(media_token = session1.media_token)
            actual2_by_media = sut.get_user_for_media_token(media_token = session2.media_token)
            actual1_by_refresh = sut.get_user_for_refresh_token(refresh_token = session1.refresh_token)
            actual2_by_refresh = sut.get_user_for_refresh_token(refresh_token = session2.refresh_token)
            actual_of_different_user_by_access = sut.get_user_for_token(session_of_different_user.access_token)
            actual_of_different_user_by_media = sut.get_user_for_media_token(session_of_different_user.media_token)
            actual_of_different_user_by_refresh = sut.get_user_for_refresh_token(session_of_different_user.refresh_token)

        self.assertEqual(expected, actual1_by_access)
        self.assertEqual(expected, actual2_by_access)
        self.assertEqual(expected, actual1_by_media)
        self.assertEqual(expected, actual2_by_media)
        self.assertEqual(expected, actual1_by_refresh)
        self.assertEqual(expected, actual2_by_refresh)
        self.assertEqual(session_of_different_user.user_id, actual_of_different_user_by_access)
        self.assertEqual(session_of_different_user.user_id, actual_of_different_user_by_media)
        self.assertEqual(session_of_different_user.user_id, actual_of_different_user_by_refresh)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_after_new_single_session_old_session_is_not_returned(self, mock_time):
        assert time.time() == 1000
        session = Session(
            user_id = 13,
            access_token = 'token',
            media_token = "media",
            refresh_token = "refresh",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        new_session = Session(
            user_id = 13,
            access_token = 'new_token',
            media_token = "new_media",
            refresh_token = "new_refresh",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        expected_old = None
        expected_new = 13
        
        with self.app.app_context():
            sut.insert_user_session(session = session)
            sut.create_new_single_session(session = new_session)
            actual_old_by_access = sut.get_user_for_token(session.access_token)
            actual_old_by_media = sut.get_user_for_media_token(session.media_token)
            actual_old_by_refresh = sut.get_user_for_refresh_token(session.refresh_token)
            actual_new_by_access = sut.get_user_for_token(new_session.access_token)
            actual_new_by_media = sut.get_user_for_media_token(new_session.media_token)
            actual_new_by_refresh = sut.get_user_for_refresh_token(new_session.refresh_token)

        self.assertEqual(expected_old, actual_old_by_access)
        self.assertEqual(expected_old, actual_old_by_media)
        self.assertEqual(expected_old, actual_old_by_refresh)
        self.assertEqual(expected_new, actual_new_by_access)
        self.assertEqual(expected_new, actual_new_by_media)
        self.assertEqual(expected_new, actual_new_by_refresh)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_after_swap_refresh_session_old_session_is_not_returned(self, mock_time):
        assert time.time() == 1000
        session = Session(
            user_id = 13,
            access_token = "token",
            media_token = "media",
            refresh_token = "refresh",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        new_session = Session(
            user_id = 13,
            access_token = "new_token",
            media_token = "new_media",
            refresh_token = "new_refresh",
            access_expires_at = 1500,
            refresh_expires_at = 5000
        )
        expected_old = None
        expected_new = 13
        
        with self.app.app_context():
            sut.insert_user_session(session = session)
            sut.swap_refresh_session(refresh_token = session.refresh_token, session = new_session)
            actual_old_by_access = sut.get_user_for_token(session.access_token)
            actual_old_by_media = sut.get_user_for_media_token(session.media_token)
            actual_old_by_refresh = sut.get_user_for_refresh_token(session.refresh_token)
            actual_new_by_access = sut.get_user_for_token(new_session.access_token)
            actual_new_by_media = sut.get_user_for_media_token(new_session.media_token)
            actual_new_by_refresh = sut.get_user_for_refresh_token(new_session.refresh_token)

        self.assertEqual(expected_old, actual_old_by_access)
        self.assertEqual(expected_old, actual_old_by_media)
        self.assertEqual(expected_old, actual_old_by_refresh)
        self.assertEqual(expected_new, actual_new_by_access)
        self.assertEqual(expected_new, actual_new_by_media)
        self.assertEqual(expected_new, actual_new_by_refresh)


if __name__ == '__main__':
    unittest.main(verbosity=2)
