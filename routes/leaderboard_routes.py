from flask import Blueprint, jsonify
from controllers.leaderboard_controller import get_leaderboard_data
from models.users_model import User
from config.db_config import db

leaderboard_routes = Blueprint('leaderboard', __name__)




@leaderboard_routes.route('/', methods=['GET'])
def leaderboard():
    data = get_leaderboard_data()
    return jsonify(data)

@leaderboard_routes.route('/<int:user_id>', methods=['DELETE'])
def delete_user_from_leaderboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Remove user and their associated data
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User removed from leaderboard"}), 200