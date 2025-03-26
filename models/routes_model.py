from config.db_config import db

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('difficulty_levels.id'), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    
    # Relationships
    difficulty = db.relationship('DifficultyLevel', backref=db.backref('routes', lazy=True))
    
    def __repr__(self):
        return f"<Route {self.id}: Type {self.type}>"