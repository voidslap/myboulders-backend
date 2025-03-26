from models.users_model import User, db

def get_all_users():
    try:
        users = User.query.all()
        return [{'id': user.id, 'username': user.username} for user in users]
    except Exception as e:
        db.session.rollback()
        return None, 'Database error'
    

def create_user(username, password):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return None, 'User already exists'
    
    new_user = User(username=username)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return {'id': new_user.id, 'username': new_user.username}, None
    except Exception as e:
        db.session.rollback()
        return None, 'Database error'
    

def get_user_by_id_or_username(user_id=None, username=None):
    if user_id:
        user = User.query.filter_by(id=user_id).first()
    elif username:
        user = User.query.filter_by(username=username).first()
    else:
        return None, 'Missing user_id or username'
    
    if user:
        return {'id': user.id, 'username': user.username, 'password_hash': user.password_hash}, None
    else:
        return None, 'User not found'
    
    