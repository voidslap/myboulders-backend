from flask import Blueprint, jsonify, request, make_response
from controllers import auth_controller
from controllers.user_controller import register_user
from controllers.auth_controller import  require_auth



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
    email = data.get('email')
    profile_image_url = data.get('profile_image_url')
    birthdate = data.get('birthdate')  # 💡 ISO-format från frontend (ex: '2000-01-01')

    if not username or not password or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    user_data, error = register_user(
        username=username,
        password=password,
        email=email,
        profile_image_url=profile_image_url,
        birthdate=birthdate
    )

    if error:
        return jsonify({'error': error}), 400
    return jsonify(user_data), 201

@auth_routes.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Returns the current user based on the JWT token.
    This route is protected and requires a valid token.
    """
    user_data, error = auth_controller.verify_jwt()
    
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({
        'id': user_data.get('id'),
        'username': user_data.get('username')
    }), 200
