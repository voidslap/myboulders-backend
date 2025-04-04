from models.goals_model import Goal
from models.users_model import User
from config.db_config import db
from sqlalchemy.sql import func
from datetime import datetime

def get_user_goals(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found'
            
        goals = Goal.query.filter_by(user_id=user_id).all()
        return [{
            'id': goal.id,
            'title': goal.title,
            'description': goal.description,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'completed': goal.status
        } for goal in goals], None
        
    except Exception as e:
        return None, f'Database error: {str(e)}'

def create_goal(user_id, goal_data):
    try:
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found'
            
        new_goal = Goal(
            user_id=user_id,
            title=goal_data['title'],
            description=goal_data.get('description', ''),
            target_date=datetime.strptime(goal_data['target_date'], '%Y-%m-%d') if goal_data.get('target_date') else None,
            status=False  # New goals start as incomplete
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        return {
            'id': new_goal.id,
            'title': new_goal.title,
            'description': new_goal.description,
            'target_date': new_goal.target_date.isoformat() if new_goal.target_date else None,
            'completed': new_goal.status
        }, None
        
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'

def update_goal(goal_id, user_id, goal_data):
    try:
        goal = Goal.query.get(goal_id)
        if not goal:
            return None, 'Goal not found'
            
        if goal.user_id != user_id:
            return None, 'Unauthorized access to this goal'
            
        goal.title = goal_data['title']
        goal.description = goal_data.get('description', '')
        goal.target_date = datetime.strptime(goal_data['target_date'], '%Y-%m-%d') if goal_data.get('target_date') else None
        
        db.session.commit()
        
        return {
            'id': goal.id,
            'title': goal.title,
            'description': goal.description,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'completed': goal.status
        }, None
        
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'

def update_goal_status(goal_id, user_id, completed):
    try:
        goal = Goal.query.get(goal_id)
        if not goal:
            return None, 'Goal not found'
            
        if goal.user_id != user_id:
            return None, 'Unauthorized access to this goal'
            
        goal.status = completed
        db.session.commit()
        
        return {
            'id': goal.id,
            'title': goal.title,
            'description': goal.description,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'completed': goal.status
        }, None
        
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'

def delete_goal(goal_id, user_id):
    try:
        goal = Goal.query.get(goal_id)
        if not goal:
            return None, 'Goal not found'
            
        if goal.user_id != user_id:
            return None, 'Unauthorized access to this goal'
            
        db.session.delete(goal)
        db.session.commit()
        
        return {'message': f'Goal {goal_id} deleted successfully'}, None
        
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'