from flask import request, jsonify
from .require_decorators import get_cropped_token
from .data.data_models import ResponseCode
from .data import dao_session
from urllib.parse import parse_qs

def handle_has_media_access():
    media_token = get_cropped_token(_get_token_from_request('Media-Authorization'))
    if (media_token is None):
        errorResponse = jsonify({'message':'Missing Authorization!','code':ResponseCode.MISSING_MEDIA_AUTHORIZATION})
        return errorResponse, 401
    user_id = dao_session.get_user_for_media_token(media_token=media_token)
    if (user_id is None):
        errorResponse = jsonify({'message':'Invalid Authorization!','code':ResponseCode.INVALID_MEDIA_AUTHORIZATION})
        return errorResponse, 401
    return jsonify({'message':'Access Granted','code': ResponseCode.SUCCESS_MEDIA_ACCESS}), 200

def _get_token_from_request(key: str):
    token = request.headers.get(key)
    if (token is not None):
        return token
    original_uri = request.headers.get('X-Original-URI')
    if not isinstance(original_uri,str):
        return None
    query_string = original_uri[original_uri.find('?')+1:]
    return _get_first_token_from_query_string(query_string = query_string, key = key)

def _get_first_token_from_query_string(query_string: str, key: str):
    query_dict = parse_qs(query_string)
    tokens = query_dict.get(key, [None])
    return tokens[0]