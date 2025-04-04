from flask import Blueprint, jsonify, request, make_response
from controllers import auth_controller
from controllers.auth_controller import authenticate_user, verify_jwt
from controllers.user_controller import create_user


# __name__  is telling Flask "where am I in the Python package structure"
auth_routes = Blueprint('auth_routes', __name__)

#Login
@auth_routes.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
        
    # Check Content-Type
    if not request.is_json:
        print(f"Invalid Content-Type: {request.headers.get('Content-Type')}")
        return jsonify({'error': 'Content-Type must be application/json'}), 415
        
    # Normal login flow
    data = request.get_json()
    print(f"Received login data: {data}")  # Add debug logging
    
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
    email = data.get('email')
    profile_image_url = data.get('profile_image_url', 'https://i.imgur.com/3sceVnu.jpeg')  # Default image if none provided

    # Validate required fields
    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields: username, password, and email'}), 400

    # Create user with all required fields
    user_data, error = create_user(username=username, password=password, email=email, profile_image_url=profile_image_url)

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
