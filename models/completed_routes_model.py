from config.db_config import db
from sqlalchemy.sql import func


class CompletedRoute(db.Model):
    __tablename__ = 'completed_routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)

    # One-to-many relation till User
    user = db.relationship('User', backref='completed_routes')

    # One-to-one relation till Route
    route = db.relationship('Route', back_populates='completed_route')