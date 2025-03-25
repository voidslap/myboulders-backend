from config.db_config import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    hashed_password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    profile_image_url = db.Column(db.String(1000))
    register_date = db.Column(db.DateTime, nullable=False, default=func.now())
    
    # Creating relationships between tables connected to User 
    achievements = db.relationship('achievements', backref='user', lazy=True)
    goals = db.relationship('goals', backref='users', lazy=True)
    climbing_sessions = db.relationship('climbing_sessions', backref='user', lazy=True)
    completed_routes = db.relationship('completed_routes', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    