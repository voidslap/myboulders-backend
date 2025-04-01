from flask import Blueprint, jsonify
from controllers.leaderboard_controller import get_leaderboard_data

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard', methods=['GET'])
def leaderboard():
    data = get_leaderboard_data()
    return jsonify(data)