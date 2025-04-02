from models.achievements_model import Achievement
from models.users_model import User
from config.db_config import db
from sqlalchemy.sql import func

def get_user_achievements(user_id):
    # Verify user authentication
    try:
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found'

        # Get achievements for the user    
        achievements = Achievement.query.filter_by(user_id=user_id).all()
        return [{
            'id': achievement.id,
            'name': achievement.achievement_name,
            'date': achievement.achievement_date.isoformat()
        } for achievement in achievements], None
        
    except Exception as e:
        return None, f'Database error: {str(e)}'

def add_achievement(user_id, achievement_name):
    try:
        user = User.query.get(user_id)
        if not user:
            return None, 'User not found'
        
        # Check if the achievement already exists for the user    
        new_achievement = Achievement(
            user_id=user_id,
            achievement_name=achievement_name
        )
        
        db.session.add(new_achievement)
        db.session.commit()
        
        return {
            'id': new_achievement.id,
            'name': new_achievement.achievement_name,
            'date': new_achievement.achievement_date.isoformat()
        }, None
        
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'