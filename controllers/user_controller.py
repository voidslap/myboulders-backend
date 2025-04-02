from models.users_model import User, db

def get_all_users():
    try:
        users = User.query.all()
        return [{'id': user.id, 'username': user.username} for user in users]
    except Exception as e:
        db.session.rollback()
        return None, 'Database error'
    

from models.users_model import User, db
from datetime import datetime

def register_user(username, password, email, profile_image_url=None, birthdate=None):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return None, 'User already exists'

    # Convert string to Python date object
    if birthdate:
        try:
            birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid birthdate format"

    new_user = User(
        username=username,
        email=email,
        profile_image_url=profile_image_url,
        birthdate=birthdate
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return {'id': new_user.id, 'username': new_user.username}, None
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'





# This function talks to the route search_user in user_routes.py
def get_user_by_id_or_username(user_id=None, username=None):
    if username:
        user = User.query.filter_by(username=username).first()
    elif user_id:
        user = User.query.filter_by(id=user_id).first()
    else:
        return None, "No identifier provided"

    if not user:
        return None, "User not found"

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_image_url": user.profile_image_url,
        "register_date": user.register_date.isoformat() if user.register_date else None,
    }

    return user_data, None

    

def delete_user(user_id=None, username=None):
    # Check if at least one parameter is provided
    if not user_id and not username:
        return None, 'Either user_id or username must be provided'

    # Search by ID if provided
    if user_id:
        user = User.query.get(user_id)  # More efficient than filter_by for ID
    # Search by username if provided
    else:
        user = User.query.filter_by(username=username).first()
    
    if not user:
        return None, 'User not found'
    
    try:
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User {user.username} deleted successfully'}, None
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'


