from config.db_config import db
from sqlalchemy.sql import func

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=False)

    