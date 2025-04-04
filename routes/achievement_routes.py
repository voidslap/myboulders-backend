from flask import Blueprint, jsonify, request
from controllers.achievement_controller import get_user_achievements, add_achievement
from utils.auth_decorator import auth_required

achievement_routes = Blueprint('achievement_routes', __name__)

# Get achievements for a specific user
@achievement_routes.route('/user/<int:user_id>', methods=['GET']) 
@auth_required
def get_achievements(user_id, current_user):
    if current_user.id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    achievements, error = get_user_achievements(user_id)
    if error:
        return jsonify({'error': error}), 404
        
    return jsonify({'achievements': achievements}), 200

@achievement_routes.route('/add', methods=['POST'])
@auth_required
def add_user_achievement(current_user):
    """Add a new achievement for the authenticated user"""
    data = request.get_json()
    if not data or 'achievement_name' not in data:
        return jsonify({'error': 'Missing achievement name'}), 400
        
    achievement, error = add_achievement(
        current_user.id, 
        data['achievement_name']
    )
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(achievement), 201