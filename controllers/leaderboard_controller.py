from models.users_model import User
from models.completed_routes_model import CompletedRoute
from config.db_config import db
from sqlalchemy import func

def get_leaderboard_data():
    result = (
        db.session.query(User.username, func.count(CompletedRoute.id).label('completed_routes_count'))
        .join(CompletedRoute)
        .group_by(User.id)
        .order_by(func.count(CompletedRoute.id).desc())
        .all()
    )

    return [{"username": r.username, "completed_routes_count": r.completed_routes_count} for r in result]