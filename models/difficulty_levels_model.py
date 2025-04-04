from config.db_config import db

class DifficultyLevel(db.Model):
    __tablename__ = 'difficulty_levels'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade = db.Column(db.String(250), nullable=False)
    
    def __repr__(self):
        return f"<DifficultyLevel {self.id}: {self.grade}>"