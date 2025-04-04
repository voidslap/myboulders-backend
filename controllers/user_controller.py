from models.users_model import User, db

def get_all_users():
    try:
        users = User.query.all()
        return [{'id': user.id, 'username': user.username} for user in users]
    except Exception as e:
        db.session.rollback()
        return None, 'Database error'
    

def create_user(username, password, email=None, profile_image_url=None):
    """
    Create a new user
    
    Args:
        username (str): The username for the new user
        password (str): The password for the new user
        email (str, optional): Email address for the new user
        profile_image_url (str, optional): URL to the user's profile image
        
    Returns:
        tuple: (user_data dict or None, error message or None)
    """
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return None, 'Username already exists'
    
    # Check if email already exists (if provided)
    if email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return None, 'Email already in use'
    
    # Set default profile image if none provided
    if not profile_image_url:
        profile_image_url = 'https://i.imgur.com/3sceVnu.jpeg'  # Default profile image
    
    # Create new user with all provided fields
    new_user = User(
        username=username,
        email=email,
        profile_image_url=profile_image_url
    )
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return {
            'id': new_user.id, 
            'username': new_user.username,
            'email': new_user.email,
            'profile_image_url': new_user.profile_image_url
        }, None
    except Exception as e:
        db.session.rollback()
        return None, f'Database error: {str(e)}'


# This function talks to the route search_user in user_routes.py
def get_user_by_id_or_username(user_id=None, username=None):
    if user_id:
        user = User.query.filter_by(id=user_id).first()
    elif username:
        user = User.query.filter_by(username=username).first()
    else:
        return None, 'Missing user_id or username'
    
    if user:
        return {'id': user.id, 'username': user.username, 'password_hash': user.hashed_password}, None
    else:
        return None, 'User not found'
    

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


