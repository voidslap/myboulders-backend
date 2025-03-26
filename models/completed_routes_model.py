from config.db_config import db

class CompletedRoute(db.Model):
    __tablename__ = 'completed_routes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    
    # Relationships
    route = db.relationship('Route', backref=db.backref('completed_by', lazy=True))
    
    def __repr__(self):
        return f"<CompletedRoute {self.id}: User {self.user_id}, Route {self.route_id}>"