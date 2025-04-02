from flask import Blueprint, jsonify, request, make_response
from controllers import auth_controller
from controllers.auth_controller import authenticate_user, verify_jwt
from controllers.user_controller import create_user


# __name__  is telling Flask "where am I in the Python package structure"
auth_routes = Blueprint('auth_routes', __name__)

#Login
@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate that required fields exist in request
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    token, error = auth_controller.authenticate_user(
        data['username'],
        data['password']
    )

    if error:
        return jsonify({'error': error}), 401

    response = make_response(jsonify({'message': 'Login successful'}))
    response.set_cookie('token', token, httponly=True)

    return response, 200

#Logout (deletes JWT-Cookie)
@auth_routes.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({'message': 'Logged out'}))
    response.set_cookie('token', '', expires=0)
    return response, 200


@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user_data, error = create_user(username=username, password=password)

    if error:
        return jsonify({'error': error}), 400
    else:
        return jsonify(user_data), 201

@auth_routes.route('/check', methods=['GET'])
def check_auth():
    """Validates if the user's JWT token is valid"""
    user_data, error = verify_jwt()
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({'authenticated': True, 'user': user_data}), 200
