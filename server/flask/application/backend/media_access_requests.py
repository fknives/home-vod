from flask import request, jsonify
from .require_decorators import get_cropped_token
from .data.data_models import ResponseCode
from .data import dao_session
from .data import dao_users

def handle_has_media_access():
    media_token = get_cropped_token(request.headers.get('Media-Authorization'))
    if (media_token is None):
        errorResponse = jsonify({'message':'Missing Authorization!','code':ResponseCode.MISSING_MEDIA_AUTHORIZATION})
        return errorResponse, 401
    user_id = dao_session.get_user_for_media_token(media_token=media_token)
    if (user_id is None):
        errorResponse = jsonify({'message':'Invalid Authorization!','code':ResponseCode.INVALID_MEDIA_AUTHORIZATION})
        return errorResponse, 401
    return jsonify({'message':'Access Granted','code': ResponseCode.SUCCESS_MEDIA_ACCESS}), 200