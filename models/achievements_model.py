from config.db_config import db
from sqlalchemy.sql import func

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_name = db.Column(db.String(50), nullable=False)
    achievement_date = db.Column(db.DateTime, nullable=False, default=func.now())