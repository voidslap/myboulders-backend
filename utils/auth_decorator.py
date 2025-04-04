from functools import wraps
from flask import request, jsonify
import jwt
from config.db_config import Config
from models.users_model import User

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Hämta token från cookies eller Authorization-header
        token = request.cookies.get('token')
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401

        try:
            # Dekryptera JWT-token
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            user = User.query.get(payload['id'])
            if not user:
                return jsonify({'error': 'User not found'}), 401

            # Lägg till den autentiserade användaren i kwargs
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    return decorated_function