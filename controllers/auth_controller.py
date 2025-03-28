import jwt
import datetime
from flask import request, jsonify
from models.users_model import User
from werkzeug.security import check_password_hash
from config.db_config import Config

def generate_jwt(user):
    payload = {
        'id': user.id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()

    if not user:
        return None, 'User not found'
    
    if not check_password_hash(user.password_hash, password):
        return None, 'Invalid password'
    
    token = generate_jwt(user)

    return token, None

def verify_jwt():
    token = request.cookies.get('token')

    if not token:
        return None, 'No token provided'
    
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return {'id': payload['id'],  'username': payload['username']}, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
    

