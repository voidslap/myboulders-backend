from config.db_config import db
from sqlalchemy.sql import func

class ClimbingSession(db.Model):
    __tablename__ = 'climbing_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=func.now())
    flash = db.Column(db.Boolean, nullable=False)
    
    # Relationships
    route = db.relationship('Route', backref=db.backref('sessions', lazy=True))
    
    def __repr__(self):
        return f"<ClimbingSession {self.id}: User {self.user_id}, Route {self.route_id}, Flash: {self.flash}>"