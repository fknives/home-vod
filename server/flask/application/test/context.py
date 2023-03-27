from backend.flask_project import create_app
from backend.data.data_models import Session

default_test_config = {
    "DATABASE_PATH": "testdb",
    "SESSION_ACCESS_EXPIRATION_IN_SECONDS": 20000,
    "SESSION_REFRESH_EXPIRATION_IN_SECONDS": 50000,
    "DATABASE_PATH": "testdb",
    "MAX_PASSWORD_LENGTH": 64,
    "MAX_USERNAME_LENGTH": 64,
    "MAX_OTP_LENGTH": 16,
    "MAX_TOKEN_LENGTH": 200,
    "KEY_LENGTH": 30,
}

def create_test_session(user_id, access_token = '', media_token = '', refresh_token = '', access_expires_at = 1, refresh_expires_at = 1):
    return Session(
        user_id = user_id,
        access_token = access_token,
        media_token = media_token,
        refresh_token = refresh_token,
        access_expires_at = access_expires_at,
        refresh_expires_at = refresh_expires_at
    )