from secrets import token_urlsafe
from flask import current_app
import time
import pyotp
from .data.data_models import Session

def _get_byte_count():
    return current_app.config.get('SECRECT_BYTE_COUNT') or 64

def _get_access_expires_in():
    return current_app.config.get('SESSION_ACCESS_EXPIRATION_IN_SECONDS') or 86400

def _get_refresh_expires_in():
    return current_app.config.get('SESSION_REFRESH_EXPIRATION_IN_SECONDS') or 2*86400

def _get_reset_password_expires_in():
    return current_app.config.get('RESET_PASSWORD_EXPIRATION_IN_SECONDS') or 2*86400

def generate_session(user_id, byte_count = None, access_expires_in = None, refresh_expires_in = None):
    byte_count = byte_count or _get_byte_count()
    access_expires_in = access_expires_in or _get_access_expires_in()
    refresh_expires_in = refresh_expires_in or _get_refresh_expires_in()
    current_time = time.time()
    return Session(
        user_id = user_id,
        access_token = token_urlsafe(byte_count),
        media_token = token_urlsafe(byte_count),
        refresh_token = token_urlsafe(byte_count),
        access_expires_at = access_expires_in + current_time,
        refresh_expires_at = refresh_expires_in + current_time,
	)

def generate_reset_password_expires_at(reset_password_expires_in = None):
    current_time = time.time()
    reset_password_expires_in = reset_password_expires_in or _get_reset_password_expires_in()
    return reset_password_expires_in + current_time

def generate_otp_secret():
    return pyotp.random_base32()

def verify_otp(secret, otp_code):
    totp = pyotp.TOTP(secret)
    timestampNow = time.time()
    return totp.verify(otp_code, time.time(), 2)

def get_url(secret, username):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username,issuer_name='FnivesVOD')
   