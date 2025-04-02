from models.routes_model import Route
from models.difficulty_levels_model import DifficultyLevel
from config.db_config import db

def create_route(route_data):
    """
    Create a new climbing route.
    
    Args:
        route_data (dict): Dictionary containing route information:
            - type (str): Route type ('boulder', 'lead', 'top-rope', etc)
            - difficulty (str): Difficulty grade ('6A', '7C+', etc)
            - location (str, optional): Location of the route
            - description (str, optional): Description of the route
            
    Returns:
        tuple: (dict, str or None)
            - On success: (route data dict, None)
            - On error: (None, error message)
    """
    try:
        # Get or create difficulty level
        difficulty = DifficultyLevel.query.filter_by(grade=route_data['difficulty']).first()
        if not difficulty:
            difficulty = DifficultyLevel(grade=route_data['difficulty'])
            db.session.add(difficulty)
            db.session.flush()  # Get ID without committing
        
        # Create new route
        new_route = Route(
            difficulty_id=difficulty.id,
            type=route_data['type']
        )
        
        db.session.add(new_route)
        db.session.commit()
        
        # Return route data
        return {
            'id': new_route.id,
            'type': new_route.type,
            'difficulty': difficulty.grade
        }, None
        
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"