from flask import Blueprint, jsonify, request
from datetime import datetime
from controllers.goals_controller import (
    get_user_goals, 
    create_goal, 
    update_goal,
    update_goal_status,
    delete_goal
)
from controllers.auth_controller import verify_jwt

goals_routes = Blueprint('goals_routes', __name__)

@goals_routes.route('/', methods=['GET'])
def get_goals():
    """Get all goals for authenticated user"""
    user_data, error = verify_jwt()
    if error:
        return jsonify({'error': error}), 401
        
    goals, error = get_user_goals(user_data['id'])
    if error:
        return jsonify({'error': error}), 404
        
    return jsonify({'goals': goals}), 200

@goals_routes.route('/', methods=['POST'])
def add_goal():
    """Create a new goal"""
    user_data, error = verify_jwt()
    if error:
        return jsonify({'error': error}), 401
        
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
        
    goal, error = create_goal(user_data['id'], data)
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(goal), 201

@goals_routes.route('/<int:goal_id>', methods=['PUT'])
def edit_goal(goal_id):
    """Update an existing goal"""
    user_data, error = verify_jwt()
    if error:
        return jsonify({'error': error}), 401
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    goal, error = update_goal(goal_id, user_data['id'], data)
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(goal), 200

@goals_routes.route('/<int:goal_id>/complete', methods=['POST'])
def complete_goal(goal_id):
    """Mark a goal as complete/incomplete"""
    user_data, error = verify_jwt()
    if error:
        return jsonify({'error': error}), 401
        
    data = request.get_json()
    if 'completed' not in data:
        return jsonify({'error': 'Missing completed status'}), 400
        
    goal, error = update_goal_status(goal_id, user_data['id'], data['completed'])
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(goal), 200

@goals_routes.route('/<int:goal_id>', methods=['DELETE'])
def remove_goal(goal_id):
    """Delete a goal"""
    user_data, error = verify_jwt()
    if error:
        return jsonify({'error': error}), 401
        
    result, error = delete_goal(goal_id, user_data['id'])
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(result), 200