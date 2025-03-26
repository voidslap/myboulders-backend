from flask import Blueprint, jsonify, request
from controllers.auth_controller import authenticate_user


auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    

    user_data, error = authenticate_user(data['username'], data['password'])

    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({'message': 'Login successful {}'.format(user_data['username'])}), 200

    