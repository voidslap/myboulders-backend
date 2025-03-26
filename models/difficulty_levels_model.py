from config.db_config import db
from sqlalchemy.sql import func

class DifficultyLevel(db.Model):
    __tablename__ = 'difficulty_levels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade = db.Column(db.String(50), nullable=False)
    # routes relationship comes from backref in Route model