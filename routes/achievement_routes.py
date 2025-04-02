from flask import Blueprint, jsonify, request
from controllers.achievement_controller import get_user_achievements, add_achievement
from controllers.auth_controller import verify_jwt

achievement_routes = Blueprint('achievement_routes', __name__)

# Get achievements for a specific user
@achievement_routes.route('/user/<int:user_id>', methods=['GET']) 
def get_achievements(user_id):
    # Verify user authentication
    user_data, auth_error = verify_jwt()
    if auth_error:
        return jsonify({'error': auth_error}), 401

    # Get achievements
    achievements, error = get_user_achievements(user_id)
    if error:
        return jsonify({'error': error}), 404
        
    return jsonify({'achievements': achievements}), 200

@achievement_routes.route('/add', methods=['POST'])
def add_user_achievement():
    # Verify user authentication
    user_data, auth_error = verify_jwt()
    if auth_error:
        return jsonify({'error': auth_error}), 401
        
    data = request.get_json()
    if not data or 'achievement_name' not in data:
        return jsonify({'error': 'Missing achievement name'}), 400
        
    achievement, error = add_achievement(
        user_data['id'], 
        data['achievement_name']
    )
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(achievement), 201