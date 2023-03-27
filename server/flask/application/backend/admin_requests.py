from flask import request, jsonify
from .require_decorators import get_cropped_username
from .require_decorators import get_cropped_otp
from . import token_generator_util
from .data import dao_registration_tokens
from .data import dao_reset_password_tokens
from .data import dao_users
from .data import dao_session
from .data.data_models import DataError
from .data.data_models import User
from .data.data_models import ResponseCode

def handle_create_registration_token(user: User):
    new_registration_token = get_cropped_otp(request.form.get('registration_token'))
    if new_registration_token is None or new_registration_token.strip() == '':
        errorResponse = jsonify({'message':'Invalid Registration Token given!','code':ResponseCode.INVALID_REGISTRATION_TOKEN})
        return errorResponse, 400

    result = dao_registration_tokens.insert_token(new_registration_token)
    if (result is DataError.REGISTRATION_CODE_ALREADY_EXISTS):
        errorResponse = jsonify({'message':'Invalid Registration Token given!','code':ResponseCode.INVALID_REGISTRATION_TOKEN})
        return errorResponse, 400

    return jsonify({'message':'Registration token Saved!','code':ResponseCode.SUCCESS_SAVED_REGISTRATION_TOKEN}), 200

def handle_create_reset_password_token(user: User):
    reset_password_token = get_cropped_otp(request.form.get('reset_password_token'))
    username_to_reset = get_cropped_username(request.form.get('username_to_reset'))
    if reset_password_token is None or reset_password_token.strip() == '':
        errorResponse = jsonify({'message':'Invalid Reset Password Token given!','code':ResponseCode.INVALID_RESET_PASSWORD_TOKEN})
        return errorResponse, 400

    if username_to_reset is None or username_to_reset.strip() == '':
        errorResponse = jsonify({'message':'username_to_reset cannot be empty!','code':ResponseCode.INVALID_USERNAME_TO_EDIT})
        return errorResponse, 400

    expires_at = token_generator_util.generate_reset_password_expires_at()

    dao_reset_password_tokens.insert_token(token = reset_password_token, username = username_to_reset, expires_at = expires_at)

    return jsonify({'message':'Reset Password token Saved!','code':ResponseCode.SUCCESS_SAVED_RESET_PASSWORD_TOKEN}), 200

def handle_reset_user_otp_verification(user: User):
    username = get_cropped_username(request.form.get('username_to_reset'))
    if username is None or username.strip() == '':
        errorResponse = jsonify({'message':'username_to_reset cannot be empty!','code':ResponseCode.INVALID_USERNAME_TO_EDIT})
        return errorResponse, 400

    user_to_update = dao_users.get_user_by_name(username)
    if user_to_update is None:
        errorResponse = jsonify({'message':'User cannot be found!','code':ResponseCode.NOT_FOUND_USER})
        return errorResponse, 400

    dao_users.update_user_otp_verification(user_to_update.id, False)

    return jsonify({'message':'OTP Verification Reset!','code':ResponseCode.SUCCESS_RESET_OTP_VERIFICATION}), 200

def handle_get_users(user: User):
    users = dao_users.get_users()
    simplified_users = map(lambda user: {'name':user.name,'privileged':user.privileged}, users)

    return jsonify({'users': list(simplified_users)}), 200

def handle_get_registration_tokens(user: User):
    tokens = dao_registration_tokens.get_tokens()

    return jsonify({'registration_tokens': list(tokens)}), 200

def handle_delete_user_by_name(user: User):
    user_name_to_delete = get_cropped_username(request.form.get('username_to_delete'))
    success_response = jsonify({'message':'User deleted!','code':ResponseCode.SUCCESS_DELETED_USER})
    if user_name_to_delete is None:
        return success_response, 200

    user_to_delete = dao_users.get_user_by_name(user_name_to_delete)
    if user_to_delete is None:
        return success_response, 200

    dao_session.delete_all_user_session_by_user_id(user_to_delete.id)
    dao_users.delete_user_by_id(user_to_delete.id)

    return success_response, 200

def handle_delete_registration_token(user: User):
    registration_token_to_delete = get_cropped_otp(request.form.get('registration_token'))
    success_response = jsonify({'message':'Token deleted!','code':ResponseCode.SUCCESS_DELETED_TOKEN})
    if registration_token_to_delete is None:
        return success_response, 200

    dao_registration_tokens.delete_token(registration_token_to_delete)

    return success_response, 200
