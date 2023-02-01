from backend.flask_project import create_app

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