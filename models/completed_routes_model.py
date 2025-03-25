from config.db_config import db
from sqlalchemy.sql import func

class CompletedRoute(db.Model):
    __tablename__ = 'completed_routes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)

    route = db.relationship('routes', back_populates='completed_routes')