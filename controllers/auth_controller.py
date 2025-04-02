import jwt
import datetime
from flask import request, jsonify
from models.users_model import User
from werkzeug.security import check_password_hash
from config.db_config import Config

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
    """Check for JWT in cookie or Authorization header"""
    # First check for token in cookie
    token = request.cookies.get('token')
    
    # If not in cookie, check Authorization header
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return None, 'No authentication token provided'
        
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
