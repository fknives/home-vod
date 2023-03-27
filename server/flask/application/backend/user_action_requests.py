from flask import request, jsonify
from .require_decorators import get_cropped_password
from .require_decorators import get_cropped_otp
from .require_decorators import get_cropped_key
from . import token_generator_util
from .data import dao_users
from .data import dao_session
from .data import dao_reset_password_tokens
from .data import dao_file_metadata_of_user
from .data import dao_file_metadata
from .data.data_models import User
from .data.data_models import ResponseCode
from .auth_requests import _jsonify_session as jsonify_session

def handle_change_password(user: User):
    password = get_cropped_password(request.form.get('password'))
    if password is None:
        errorResponse = jsonify({'message':'Invalid Password!','code':ResponseCode.INVALID_PASSWORD})
        return errorResponse, 400

    new_password = get_cropped_password(request.form.get('new_password'))
    if new_password is None:
        errorResponse = jsonify({'message':'New Password cannot be empty!','code':ResponseCode.INVALID_NEW_PASSWORD})
        return errorResponse, 400

    foundUser = dao_users.get_user_by_name_and_password(user_name = user.name, password = password)
    if (foundUser is None):
        errorResponse = jsonify({'message':'Invalid Password!','code':ResponseCode.INVALID_PASSWORD})
        return errorResponse, 400
        
    session = token_generator_util.generate_session(user.id)
    dao_users.update_user_password(user_id = user.id, new_password = new_password)
    dao_session.create_new_single_session(session = session)
    return jsonify_session(session), 200

def handle_reset_password(username: str, password: str):
    reset_password_token = get_cropped_otp(request.form.get('reset_password_token'))
    if reset_password_token is None:
        errorResponse = jsonify({'message':'Invalid Reset Password Token given!','code':ResponseCode.UNKNOWN_RESET_PASSWORD_TOKEN})
        return errorResponse, 400

    if dao_reset_password_tokens.is_valid_token(token = reset_password_token, username = username) is False:
        errorResponse = jsonify({'message':'Invalid Reset Password Token given!','code':ResponseCode.UNKNOWN_RESET_PASSWORD_TOKEN})
        return errorResponse, 400

    foundUser = dao_users.get_user_by_name(username = username)
    if (foundUser is None):
        errorResponse = jsonify({'message':'User cannot be found!','code':ResponseCode.NOT_FOUND_USER})
        return errorResponse, 400

    dao_users.update_user_password(user_id = foundUser.id, new_password = password)

    dao_reset_password_tokens.delete_tokens(username = username)

    return jsonify({'message':'Password was Saved!','code':ResponseCode.SUCCESS_SAVED_PASSWORD}), 200

def handle_get_is_user_priviliged(user: User):
    return jsonify({'is_privileged': user.privileged}), 200

def handle_add_user_file_data(user: User):
    metadata_to_save = request.get_json(force=True, silent = True)
    if (metadata_to_save is not None and isinstance(metadata_to_save,dict)):
        dao_file_metadata_of_user.insert_metadata(user_id = user.id, metadata = metadata_to_save)
        return jsonify({'message': 'User\'s File MetaData Saved!', 'code': ResponseCode.SUCCESS_SAVED_USER_FILE_METADATA}), 200
    return jsonify({'message': 'Couldn\'t save user\'s metadata!', 'code': ResponseCode.CANT_SAVE_USER_FILE_METADATA}), 400

def handle_get_user_file_data(user: User):
    return jsonify(dao_file_metadata_of_user.get_metadata(user_id = user.id)), 200


def handle_add_file_metadata(user: User):
    metadata_to_save = request.get_json(force=True, silent = True)
    if (metadata_to_save is not None and isinstance(metadata_to_save,dict)):
        dao_file_metadata.insert_metadata(metadata = metadata_to_save)
        return jsonify({'message': 'File MetaData Saved!', 'code': ResponseCode.SUCCESS_SAVED_FILE_METADATA}), 200
    return jsonify({'message': 'Couldn\'t save metadata!', 'code': ResponseCode.CANT_SAVE_FILE_METADATA}), 400


def handle_get_file_metadata(user: User):
    file_key = get_cropped_key(request.args.get('file_key'))
    if (file_key is None):
        return jsonify({'message': 'Invalid FileKey (file_key)!', 'code': ResponseCode.INVALID_FILE_KEY}), 400        
    return jsonify(dao_file_metadata.get_metadata(file_key = file_key)), 200    