from flask import request, jsonify
from .require_decorators import get_cropped_otp
from .require_decorators import get_cropped_token
from . import token_generator_util
from .data import dao_registration_tokens
from .data import dao_users
from .data import dao_session
from .data.data_models import DataError
from .data.data_models import RegisteringUser
from .data.data_models import User
from .data.data_models import ResponseCode

def handle_register(username, password):
    one_time_password = get_cropped_otp(request.form.get('otp') or '')
    if not dao_registration_tokens.is_valid_token(one_time_password):
        errorResponse = jsonify({'message':'Invalid Token!','code':ResponseCode.UNKNOWN_REGISTRATION_TOKEN})
        return errorResponse, 400

    one_time_password_secret = token_generator_util.generate_otp_secret()
    user = RegisteringUser(name = username, password = password, otp_secret = one_time_password_secret)
    result = dao_users.insert_user(user)
    if (result is DataError.USER_NAME_NOT_VALID):
        errorResponse = jsonify({'message':'Username is already taken!','code':ResponseCode.ALREADY_TAKEN_USERNAME})
        return errorResponse, 400

    dao_registration_tokens.delete_token(one_time_password)
    secret_url = token_generator_util.get_url(user.name, one_time_password_secret)
    return jsonify({'otp_secret': secret_url}), 200

def handle_login(user: User):
    if user.was_otp_verified:
        successResponse = jsonify({'message':'User found!','code':ResponseCode.SUCCESS_FOUND_USER})
        return successResponse, 200
    else:
        secret_url = token_generator_util.get_url(username=user.name, secret=user.otp_secret)
        return jsonify({'otp_secret': secret_url}), 200

def handle_otp_verification(user: User):
    one_time_password = get_cropped_otp(request.form.get('otp') or '')
    is_otp_ok = token_generator_util.verify_otp(user.otp_secret, one_time_password)
    if (is_otp_ok):
        dao_users.update_user_otp_verification(user.id, True)
        session = token_generator_util.generate_session(user.id)
        dao_session.insert_user_session(session)
        sessionResponse = jsonify({
            'access_token': session.access_token,
            'refresh_token': session.refresh_token,
            'expires_at': session.access_expires_at
        })
        return sessionResponse, 200
    else:
        errorResponse = jsonify({'message':'Invalid Token!','code':ResponseCode.INVALID_OTP})
        return errorResponse, 400

def handle_logout():
    access_token = get_cropped_token(request.headers.get('Authorization'))
    if (access_token is None):
        return '', 200
    else:
        dao_session.delete_user_session(access_token = access_token)
        return '', 200

def handle_refresh_token():
    refresh_token = get_cropped_token(request.form.get('refresh_token'))
    if refresh_token is None:
        errorResponse = jsonify({'message':'Invalid Refresh Token!','code':ResponseCode.INVALID_REFRESH_TOKEN})
        return errorResponse, 400

    user_id = dao_session.get_user_for_refresh_token(refresh_token)
    if user_id is None:
        errorResponse = jsonify({'message':'Invalid Refresh Token!','code':ResponseCode.INVALID_REFRESH_TOKEN})
        return errorResponse, 400
        
    new_session = token_generator_util.generate_session(user_id)
    dao_session.swap_refresh_session(refresh_token = refresh_token, session = new_session)
        
    sessionResponse = jsonify({
        'access_token': new_session.access_token,
        'refresh_token': new_session.refresh_token,
        'expires_at': new_session.access_expires_at
    })
    return sessionResponse, 200