from config.db_config import db
from sqlalchemy.sql import func

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('difficulty_levels.id'), nullable=False)
    type = db.Column(db.String(100), nullable=False)

    # One-to-One relationship with CompletedRoute
    completed_route = db.relationship('CompletedRoute', uselist=False, back_populates='route')
    # One-to-Many relationship with DifficultyLevel
    difficulty = db.relationship('DifficultyLevel', backref='routes')
    # One-to-Many relationship with ClimbingSession
    climbing_sessions = db.relationship('ClimbingSession', back_populates='route')