from flask import Blueprint, jsonify, request
from datetime import datetime
from controllers.goals_controller import (
    get_user_goals, 
    create_goal, 
    update_goal,
    update_goal_status,
    delete_goal
)
from utils.auth_decorator import auth_required

goals_routes = Blueprint('goals_routes', __name__)

@goals_routes.route('/', methods=['GET'])
@auth_required
def get_goals(current_user):
    """Get all goals for authenticated user"""
    goals, error = get_user_goals(current_user.id)
    if error:
        return jsonify({'error': error}), 404
        
    return jsonify({'goals': goals}), 200

@goals_routes.route('/', methods=['POST'])
@auth_required
def add_goal(current_user):
    """Create a new goal"""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
        
    goal, error = create_goal(current_user.id, data)
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(goal), 201

@goals_routes.route('/<int:goal_id>', methods=['PUT'])
@auth_required
def edit_goal(current_user, goal_id):
    """Update an existing goal"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    goal, error = update_goal(goal_id, current_user.id, data)
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(goal), 200

@goals_routes.route('/<int:goal_id>/complete', methods=['POST'])
@auth_required
def complete_goal(current_user, goal_id):
    """Mark a goal as complete/incomplete"""
    data = request.get_json()
    if 'completed' not in data:
        return jsonify({'error': 'Missing completed status'}), 400
        
    goal, error = update_goal_status(goal_id, current_user.id, data['completed'])
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(goal), 200

@goals_routes.route('/<int:goal_id>', methods=['DELETE'])
@auth_required
def remove_goal(current_user, goal_id):
    """Delete a goal"""
    result, error = delete_goal(goal_id, current_user.id)
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify(result), 200