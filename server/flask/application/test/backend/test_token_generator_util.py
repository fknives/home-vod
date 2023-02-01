import context
import unittest
import unittest.mock
from copy import copy
from flask import current_app

import backend.token_generator_util as sut


class SessionDAOTest(unittest.TestCase):

    app = context.create_app({**context.default_test_config, "SECRECT_BYTE_COUNT": 52})

    @unittest.mock.patch('time.time', return_value=1000)
    def test_session_generated_is_proper(self, mock_time):
        expected = None
        user_id = 123
        
        with self.app.app_context():
            actual = sut.generate_session(user_id)

        self.assertEqual(20000+1000, actual.access_expires_at)
        self.assertEqual(50000+1000, actual.refresh_expires_at)
        self.assertEqual(user_id, actual.user_id)
        self.assertEqual(70, len(actual.access_token))
        self.assertEqual(70, len(actual.refresh_token))

    @unittest.mock.patch('time.time', return_value=1000)
    def test_two_sessions_are_not_equal(self, mock_time):
        expected = None
        user_id = 123
        
        with self.app.app_context():
            session1 = sut.generate_session(user_id)
            session2 = sut.generate_session(user_id)

        session1Copy = copy(session1)
        self.assertEqual(session1Copy, session1)
        self.assertIsNot(session1Copy, session1)
        self.assertNotEqual(session1, session2)

    @unittest.mock.patch('time.time', return_value=1000)
    def test_two_sessions_are_not_equal(self, mock_time):
        # how to get values = pyotp.TOTP('base32secret3232').at(1000+90)
        secret = 'base32secret3232'
        nowCode = 585501
        nowMinus30SecCode = 572292
        nowMinus60SecCode = 512128
        nowMinus90SecCode = 440932
        nowPlus30SecCode = 602066
        nowPlus60SecCode = 893795
        nowPlus90SecCode = 11418
        with self.app.app_context():
            actual = sut.verify_otp(secret, nowCode)
            actual30SecBefore = sut.verify_otp(secret, nowMinus30SecCode)
            actual60SecBefore = sut.verify_otp(secret, nowMinus60SecCode)
            actual90SecBefore = sut.verify_otp(secret, nowMinus90SecCode)
            actual30SecAfter = sut.verify_otp(secret, nowPlus30SecCode)
            actual60SecAfter = sut.verify_otp(secret, nowPlus60SecCode)
            actual90SecAfter = sut.verify_otp(secret, nowPlus90SecCode)

        self.assertEqual(True, actual)
        self.assertEqual(True, actual30SecBefore)
        self.assertEqual(True, actual60SecBefore)
        self.assertEqual(True, actual30SecAfter)
        self.assertEqual(True, actual60SecAfter)
        self.assertEqual(False, actual90SecBefore)
        self.assertEqual(False, actual90SecAfter)

    def test_url_is_proper(self):
        secret = 'base32secret3232'
        actual = sut.get_url(secret=secret, username='admin')
        # URL can be verified by using text->QR code on https://www.the-qrcode-generator.com/
        self.assertEqual('otpauth://totp/FnivesVOD:admin?secret=base32secret3232&issuer=FnivesVOD', actual)


if __name__ == '__main__':
    unittest.main(verbosity=2)
