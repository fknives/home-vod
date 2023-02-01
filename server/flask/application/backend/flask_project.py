from os import path

from flask import Flask
import json
from .data import db as db
from .data.data_models import User
from .require_decorators import require_username_and_password
from .require_decorators import require_user_exists_by_username_and_password
from .require_decorators import requires_session
from .require_decorators import require_otp_verification_after_session
from .require_decorators import require_user_priviliged_after_session
from . import auth_requests as auth_requests_handler
from . import admin_requests as admin_requests_handler
from . import user_action_requests as user_action_requests_handler

# for chrome to accept the certificate run in console `endCommand(SecurityInterstitialCommandId.CMD_PROCEED)`
# to restart = `uwsgi --ini home-vod-server.ini` like in Dockerimage
def create_app(test_config=None):
    app = Flask(__name__)
    if (test_config == None):
        app.config.from_file('config.json', silent=True, load=json.load)
    else:
        app.config.from_mapping(test_config)
    db.init_app(app)

#   region auth requests
    @app.route("/register", methods=['POST'])
    @require_username_and_password
    def register(username, password):
        return auth_requests_handler.handle_register(username = username, password = password)
    
    @app.route("/otp_verification", methods=['POST'])
    @require_username_and_password
    @require_user_exists_by_username_and_password
    def otp_verification(user: User):
        return auth_requests_handler.handle_otp_verification(user = user)
        
    @app.route("/login", methods=['POST'])
    @require_username_and_password
    @require_user_exists_by_username_and_password
    def login(user: User):
        return auth_requests_handler.handle_login(user = user)

    @app.route("/logout", methods=['POST'])
    def logout():
        return auth_requests_handler.handle_logout()

    @app.route("/refresh/token", methods=['POST'])
    def refresh_token():
        return auth_requests_handler.handle_refresh_token()
#   endregion

#   region user_actions
    @app.route("/user/is_privileged", methods=['GET'])
    @requires_session
    def get_is_user_priviliged(user: User):
        return user_action_requests_handler.handle_get_is_user_priviliged(user = user)

    @app.route("/change/password", methods=['POST'])
    @requires_session
    @require_otp_verification_after_session
    def change_password(user: User):
        return user_action_requests_handler.handle_change_password(user = user)

    @app.route("/reset/password", methods=['POST'])
    @require_username_and_password
    def reset_password(username, password):
        return user_action_requests_handler.handle_reset_password(username = username, password = password)

    @app.route("/user/file/metadata", methods=['POST'])
    @requires_session
    def add_user_file_data(user: User):
        return user_action_requests_handler.handle_add_user_file_data(user = user)

    @app.route("/user/file/metadata", methods=['GET'])
    @requires_session
    def get_user_file_data(user: User):
        return user_action_requests_handler.handle_get_user_file_data(user = user)

    @app.route("/file/metadata", methods=['POST'])
    @requires_session
    def add_file_metadata(user: User):
        return user_action_requests_handler.handle_add_file_metadata(user = user)
    
    @app.route("/file/metadata", methods=['GET'])
    @requires_session
    def get_file_metadata(user: User):
        return user_action_requests_handler.handle_get_file_metadata(user = user)
#   endregion

#   region admin requests
    @app.route("/admin/registration_token", methods=['POST'])
    @requires_session
    @require_otp_verification_after_session
    @require_user_priviliged_after_session
    def create_registration_token(user: User):
        return admin_requests_handler.handle_create_registration_token(user = user)

    @app.route("/admin/reset_password_token", methods=['POST'])
    @requires_session
    @require_otp_verification_after_session
    @require_user_priviliged_after_session
    def create_reset_password_token(user: User):
        return admin_requests_handler.handle_create_reset_password_token(user = user)

    @app.route("/admin/reset_otp_verification", methods=['POST'])
    @requires_session
    @require_otp_verification_after_session
    @require_user_priviliged_after_session
    def reset_user_otp_verification(user: User):
        return admin_requests_handler.handle_reset_user_otp_verification(user = user)

    @app.route("/admin/get_users", methods=['GET'])
    @requires_session
    @require_user_priviliged_after_session
    def get_users(user: User):
        return admin_requests_handler.handle_get_users(user = user)

    @app.route("/admin/get_registration_tokens", methods=['GET'])
    @requires_session
    @require_user_priviliged_after_session
    def get_registration_tokens(user: User):
        return admin_requests_handler.handle_get_registration_tokens(user = user)

    @app.route("/admin/delete/user", methods=['POST'])
    @requires_session
    @require_otp_verification_after_session
    @require_user_priviliged_after_session
    def delete_user_by_name(user: User):
        return admin_requests_handler.handle_delete_user_by_name(user = user)
    
    @app.route("/admin/delete/registration_token", methods=['POST'])
    @requires_session
    @require_otp_verification_after_session
    @require_user_priviliged_after_session
    def delete_registration_token(user: User):
        return admin_requests_handler.handle_delete_registration_token(user = user)
#   endregion

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0')