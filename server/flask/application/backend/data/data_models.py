from enum import Enum
from enum import IntEnum

class Session:
    def __init__(self, user_id, access_token, refresh_token, access_expires_at, refresh_expires_at):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.access_expires_at = access_expires_at
        self.refresh_expires_at = refresh_expires_at

    def __eq__(self, other): 
        if not isinstance(other, Session):
            return False
        return self.user_id == other.user_id \
            and self.access_token == other.access_token \
            and self.refresh_token == other.refresh_token \
            and self.access_expires_at == other.access_expires_at \
            and self.refresh_expires_at == other.refresh_expires_at \
    
    def __str__(self):
        return 'Session(user_id={},access_token={},refresh_token={},access_expires_at={},refresh_expires_at={})'.format(self.user_id, self.access_token, self.refresh_token, self.access_expires_at, self.refresh_expires_at)

    def __repr__(self):
        return self.__str__()

class RegisteringUser:
    def __init__(self, name, password, otp_secret, privileged = False, was_otp_verified = False):
        self.name = name
        self.password = password
        self.otp_secret = otp_secret
        self.privileged = privileged
        self.was_otp_verified = was_otp_verified

    def __eq__(self, other): 
        if not isinstance(other, User):
            return False

        return self.name == other.name \
            and self.password == other.password \
            and self.otp_secret == other.otp_secret \
            and self.privileged == other.privileged \
            and self.was_otp_verified == other.was_otp_verified \

    def __str__(self):
        return 'User(name={},pass={},otp={},privileged={},otp_active={})'\
        .format(self.name, self.password, self.otp_secret, self.privileged, self.was_otp_verified)

    def __repr__(self):
        return self.__str__()

class User:
    def __init__(self, id, name, otp_secret, privileged, was_otp_verified):
        self.id = id
        self.name = name
        self.otp_secret = otp_secret
        self.privileged = privileged
        self.was_otp_verified = was_otp_verified

    def __eq__(self, other): 
        if not isinstance(other, User):
            return False

        return self.id == other.id \
            and self.name == other.name \
            and self.otp_secret == other.otp_secret \
            and self.privileged == other.privileged \
            and self.was_otp_verified == other.was_otp_verified \

    def __str__(self):
        return 'User(id={},name={},otp={},privileged={},otp_active={})'\
        .format(self.id, self.name, self.otp_secret, self.privileged, self.was_otp_verified)

    def __repr__(self):
        return self.__str__()

class DataError(Enum):
    USER_NAME_NOT_VALID = 1
    REGISTRATION_CODE_ALREADY_EXISTS = 2

class ResponseCode(IntEnum):
    SUCCESS_FOUND_USER = 200
    SUCCESS_SAVED_PASSWORD = 201
    SUCCESS_SAVED_USER_FILE_METADATA = 202
    SUCCESS_SAVED_FILE_METADATA = 203
    SUCCESS_SAVED_REGISTRATION_TOKEN = 205
    SUCCESS_DELETED_USER = 206
    SUCCESS_RESET_OTP_VERIFICATION = 207
    SUCCESS_SAVED_RESET_PASSWORD_TOKEN = 208
    SUCCESS_DELETED_TOKEN = 209


    ALREADY_TAKEN_USERNAME = 411
    NOT_FOUND_USER = 412
    INVALID_USERNAME_TO_EDIT = 413
    CANT_SAVE_USER_FILE_METADATA = 414
    CANT_SAVE_FILE_METADATA = 415
    INVALID_FILE_KEY = 416
    INVALID_PASSWORD = 421
    INVALID_NEW_PASSWORD = 422
    UNKNOWN_REGISTRATION_TOKEN = 430
    INVALID_OTP = 431
    INVALID_REFRESH_TOKEN = 450
    INVALID_RESET_PASSWORD_TOKEN = 459
    INVALID_REGISTRATION_TOKEN = 460
    UNKNOWN_RESET_PASSWORD_TOKEN = 461