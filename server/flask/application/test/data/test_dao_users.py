import os,sys
sys.path.append('../')
import context
import unittest
import unittest.mock
import time
from flask import current_app
from backend.data import db
from backend.data.data_models import RegisteringUser
from backend.data.data_models import User
from backend.data.data_models import DataError

import backend.data.dao_users as sut

class RegistrationTokenDAOTest(unittest.TestCase):

    app = context.create_app(context.default_test_config)

    def setUp(self):
        with self.app.app_context():
            db.init_db()
    
    def tearDown(self):
        with self.app.app_context():
            db.close_db()
        os.remove("testdb")
    
    def test_empty_db_contains_no_user(self):
        user_id = 1
        
        with self.app.app_context():
            actual = sut.get_user_by_id(user_id)

        self.assertEqual(None, actual)

    def test_user_inserted_can_be_found_by_id(self):
        inserted = RegisteringUser(
            name = "admin",
            password = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        expected = User(
            id = 1,
            name = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        
        with self.app.app_context():
            user_id = sut.insert_user(inserted)
            actual = sut.get_user_by_id(user_id)

        self.assertEqual(expected.id, user_id)
        self.assertEqual(expected, actual)

    def test_deleted_user_cannot_be_found(self):
        inserted = RegisteringUser(
            name = "admin",
            password = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        expected = None
        
        with self.app.app_context():
            user_id = sut.insert_user(inserted)
            sut.delete_user_by_id(user_id)
            actual = sut.get_user_by_id(user_id)

        self.assertEqual(expected, actual)

    def test_user_inserted_can_be_found_by_name(self):
        inserted = RegisteringUser(
            name = "admin",
            password = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        expected = User(
            id = 1,
            name = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        
        with self.app.app_context():
            user_id = sut.insert_user(inserted)
            actual = sut.get_user_by_name('admin')

        self.assertEqual(expected.id, user_id)
        self.assertEqual(expected, actual)

    def test_2_user_inserted_can_be_found_by_id(self):
        inserted1 = RegisteringUser(
            name = "admin",
            password = "pass",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        expected1 = User(
            id = 1,
            name = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        inserted2 = RegisteringUser(
            name = "admin2",
            password = "pass",
            otp_secret = "secret",
            privileged = False,
        )
        expected2 = User(
            id = 2,
            name = "admin2",
            otp_secret = "secret",
            privileged = False,
            was_otp_verified = False
        )
        
        with self.app.app_context():
            user_id1 = sut.insert_user(inserted1)
            actual1 = sut.get_user_by_id(user_id1)
            user_id2 = sut.insert_user(inserted2)
            actual2 = sut.get_user_by_id(user_id2)

        self.assertEqual(expected1.id, user_id1)
        self.assertEqual(expected1, actual1)
        self.assertEqual(expected2.id, user_id2)
        self.assertEqual(expected2, actual2)

    def test_2_user_inserted_can_be_get(self):
        inserted1 = RegisteringUser(
            name = "admin",
            password = "pass",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        expected1 = User(
            id = 1,
            name = "admin",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = True
        )
        inserted2 = RegisteringUser(
            name = "admin2",
            password = "pass",
            otp_secret = "secret",
            privileged = False,
        )
        expected2 = User(
            id = 2,
            name = "admin2",
            otp_secret = "secret",
            privileged = False,
            was_otp_verified = False
        )
        
        with self.app.app_context():
            user_id1 = sut.insert_user(inserted1)
            user_id2 = sut.insert_user(inserted2)
            actual = sut.get_users()

        self.assertEqual([expected1,expected2], list(actual))


    def test_user_inserted_can_not_be_found_by_good_name_and_wrong_password(self):
        inserted = RegisteringUser(
            name = "admin",
            password = "pass",
            otp_secret = "secret"
        )
        with self.app.app_context():
            sut.insert_user(inserted)
            actual = sut.get_user_by_name_and_password('admin', 'pass2')

        self.assertEqual(None, actual)

    def test_user_inserted_can_not_be_found_by_wrong_name_and_good_password(self):
        inserted = RegisteringUser(
            name = "admin",
            password = "pass",
            otp_secret = "secret"
        )
        with self.app.app_context():
            sut.insert_user(inserted)
            actual = sut.get_user_by_name_and_password('admin2', 'pass')

        self.assertEqual(None, actual)


    def test_user_inserted_can_be_found_by_name_and_password(self):
        inserted = RegisteringUser(
            name = "admin",
            password = "pass",
            otp_secret = "secret"
        )
        expected = User(
            id = 1,
            name = "admin",
            otp_secret = "secret",
            privileged = False,
            was_otp_verified = False
        )
        
        with self.app.app_context():
            sut.insert_user(inserted)
            actual = sut.get_user_by_name_and_password('admin', 'pass')

        self.assertEqual(expected, actual)

    def test_update_user_privilige(self):
        user = RegisteringUser(
            name = "admin2",
            password = "pass",
            otp_secret = "secret"
        )
        expected = User(
            id = 1,
            name = "admin2",
            otp_secret = "secret",
            privileged = True,
            was_otp_verified = False
        )
        
        with self.app.app_context():
            user_id = sut.insert_user(user)
            sut.update_user_privilige(user_id, True)
            actual = sut.get_user_by_id(user_id)
        
        self.assertEqual(expected, actual)
    
    def test_update_user_otp_verification(self):
        user = RegisteringUser(
            name = "admin2",
            password = "pass",
            otp_secret = "secret"
        )
        expected = User(
            id = 1,
            name = "admin2",
            otp_secret = "secret",
            privileged = False,
            was_otp_verified = True
        )
        
        with self.app.app_context():
            user_id = sut.insert_user(user)
            sut.update_user_otp_verification(user_id, True)
            actual = sut.get_user_by_id(user_id)
        
        self.assertEqual(expected, actual)

    def test_insert_user_twice(self):
        user = RegisteringUser(
            name = "admin2",
            password = "pass",
            otp_secret = "secret"
        )
        
        with self.app.app_context():
            sut.insert_user(user)
            actual = sut.insert_user(user)

        self.assertEqual(DataError.USER_NAME_NOT_VALID, actual)

    def test_update_user_password(self):
        user = RegisteringUser(
            name = "admin2",
            password = "pass",
            otp_secret = "secret"
        )
        expected_old = None
        expected_new = User(
            id = 1,
            name = "admin2",
            otp_secret = "secret",
            privileged = False,
            was_otp_verified = False
        )
        
        with self.app.app_context():
            user_id = sut.insert_user(user)
            sut.update_user_password(user_id = user_id, new_password = "alma")
            actual_old = sut.get_user_by_name_and_password(user_name = "admin2", password = "pass")
            actual_new = sut.get_user_by_name_and_password(user_name = "admin2", password = "alma")
        
        self.assertEqual(expected_old, actual_old)
        self.assertEqual(expected_new, actual_new)

if __name__ == '__main__':
    unittest.main(verbosity=2)
