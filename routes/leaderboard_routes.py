from flask import Blueprint, jsonify
from controllers.leaderboard_controller import get_leaderboard_data

leaderboard_routes = Blueprint('leaderboard', __name__)




@leaderboard_routes.route('/', methods=['GET'])
def leaderboard():
    data = get_leaderboard_data()
    return jsonify(data)