from flask import Blueprint, jsonify, request
from controllers.user_controller import create_user, get_user_by_id_or_username, update_user, delete_user

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/search', methods=['GET'])
def search_user():
    user_id = request.args.get('user_id')
    username = request.args.get('username')

    # The func get_user_by_id_or_username is in the user_controller.py
    user_data, error = get_user_by_id_or_username(user_id=user_id, username=username)

    if error:
        return jsonify({'error': error}), 404
    else:
        return jsonify(user_data), 200
    
