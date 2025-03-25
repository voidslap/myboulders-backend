from flask import Blueprint, jsonify, request


auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Add authenticate_user function here from controllers

    # Add error handling

    # Return 


    