from flask import Blueprint, jsonify, request
from controllers.user_controller import create_user, get_user_by_id_or_username, delete_user


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
    
    
@user_routes.route("/delete", methods=["DELETE"])
def delete_user_route():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    
    # Convert user_id to integer if it exists
    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user ID format"}), 400
            
    # Check if at least one identifier is provided
    if not user_id and not username:
        return jsonify({"error": "Either user_id or username must be provided"}), 400
        
    result, error = delete_user(user_id=user_id, username=username)
    
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result), 200



