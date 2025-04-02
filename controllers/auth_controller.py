import jwt
import datetime
from flask import request, jsonify, redirect
from models.users_model import User
from werkzeug.security import check_password_hash
from config.db_config import Config
from functools import wraps
from flask import request, jsonify

# 🔐 Generate JWT token
def create_jwt_token(user_id, username):
    payload = {
        'id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

# ✅ Handle login
def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None, "User not found"

    if not user.check_password(password):
        return None, "Invalid password"

    token = create_jwt_token(user.id, user.username)
    return token, None

# 🔍 Token verification
def verify_jwt():
    token = request.cookies.get('token')

    if not token:
        return None, 'No token provided'

    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return {'id': payload['id'], 'username': payload['username']}, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_data, error = verify_jwt()

        if error:
            return jsonify({'error': error}), 401

        # Sätt användarens data i request context om du vill (valfritt)
        request.user = token_data
        return f(*args, **kwargs)
    
    return decorated_function
