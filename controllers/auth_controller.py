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


