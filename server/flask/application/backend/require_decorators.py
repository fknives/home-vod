from flask import request, jsonify, current_app
import functools
from . import token_generator_util
from .data import dao_users
from .data.data_models import User
from .data import dao_session

def get_cropped_username(username: str):
    max_length = current_app.config['MAX_USERNAME_LENGTH']
    if (isinstance(username, str)):
        return username[0:max_length]
    else:
        return None

def get_cropped_password(password: str):
    max_length = current_app.config['MAX_PASSWORD_LENGTH']
    if (isinstance(password, str)):
        return password[0:max_length]
    else:
        return None

def get_cropped_otp(otp: str):
    max_length = current_app.config['MAX_OTP_LENGTH']
    if (isinstance(otp, str)):
        return otp[0:max_length]
    else:
        return None

def get_cropped_token(token: str):
    max_length = current_app.config['MAX_TOKEN_LENGTH']
    if (isinstance(token, str)):
        return token[0:max_length]
    else:
        return None

def get_cropped_key(key: str):
    max_length = current_app.config['KEY_LENGTH']
    if (isinstance(key, str)):
        return key[0:max_length]
    else:
        return None

def require_username_and_password(request_processor):
    @functools.wraps(request_processor)
    def do_require_username_and_password():
        username = request.form.get('username')
        if username is None:
            errorResponse = jsonify({'message':'Username cannot be empty!','code':410})
            return errorResponse, 400
        
        password = request.form.get('password')
        if password is None:
            errorResponse = jsonify({'message':'Password cannot be empty!','code':420})
            return errorResponse, 400
        return request_processor(get_cropped_username(username), get_cropped_password(password))
    return do_require_username_and_password

def require_user_exists_by_username_and_password(request_processor):
    @functools.wraps(request_processor)
    def do_require_user(username, password):
        user = dao_users.get_user_by_name_and_password(user_name = username, password = password)
        if user is None:
            errorResponse = jsonify({'message':'User cannot be found!','code':412})
            return errorResponse, 400
        return request_processor(user)
    return do_require_user

def requires_session(request_processor):
    @functools.wraps(request_processor)
    def do_require_session():
        access_token = get_cropped_token(request.headers.get('Authorization'))
        if (access_token is None):
            errorResponse = jsonify({'message':'Missing Authorization!','code':440})
            return errorResponse, 401

        user_id = dao_session.get_user_for_token(access_token)
        if (user_id is None):
            errorResponse = jsonify({'message':'Invalid Authorization!','code':441})
            return errorResponse, 401

        user = dao_users.get_user_by_id(user_id)
        if user is None:
            errorResponse = jsonify({'message':'Invalid Authorization!','code':442})
            return errorResponse, 400
        return request_processor(user)
    return do_require_session

def require_otp_verification_after_session(request_processor):
    @functools.wraps(request_processor)
    def do_require_otp(user: User):
        one_time_password = get_cropped_otp(request.form.get('otp') or '')
        is_otp_ok = token_generator_util.verify_otp(user.otp_secret, one_time_password)
        if not is_otp_ok:
            errorResponse = jsonify({'message':'Invalid Token!','code':431})
            return errorResponse, 400

        return request_processor(user)
    return do_require_otp

def require_user_priviliged_after_session(request_processor):
    @functools.wraps(request_processor)
    def do_require_user_priviliged(user: User):
        if not user.privileged:
            errorResponse = jsonify({'message':'Not Authorized!','code':460})
            return errorResponse, 400
        return request_processor(user)

    return do_require_user_priviliged