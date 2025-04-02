from app import app, db
from models.users_model import User
from models.difficulty_levels_model import DifficultyLevel
from models.routes_model import Route
from models.completed_routes_model import CompletedRoute
from models.goals_model import Goal
from models.achievements_model import Achievement
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_test_data():
    with app.app_context():
        print("Creating test data...")
        
        # Add difficulty levels if they don't exist
        if DifficultyLevel.query.count() == 0:
            difficulty_levels = [
                DifficultyLevel(grade="4"),
                DifficultyLevel(grade="5"),
                DifficultyLevel(grade="5+"),
                DifficultyLevel(grade="6A"),
                DifficultyLevel(grade="6A+"),
                DifficultyLevel(grade="6B"),
                DifficultyLevel(grade="6B+"),
                DifficultyLevel(grade="6C"),
                DifficultyLevel(grade="6C+"),
                DifficultyLevel(grade="7A"),
                DifficultyLevel(grade="7A+"),
                DifficultyLevel(grade="7B"),
                DifficultyLevel(grade="7B+"),
                DifficultyLevel(grade="7C"),
                DifficultyLevel(grade="7C+"),
                DifficultyLevel(grade="8A"),
                DifficultyLevel(grade="8A+"),
                DifficultyLevel(grade="8B"),
                DifficultyLevel(grade="8B+")
            ]
            db.session.add_all(difficulty_levels)
            db.session.commit()
            print(f"Added {len(difficulty_levels)} difficulty levels")

        # Check if test user already exists
        test_user = User.query.filter_by(username="test").first()
        if not test_user:
            # Create test user
            test_user = User(
                username="test", 
                hashed_password=generate_password_hash("test123"),
                email="test@example.com",
                profile_image_url="https://i.imgur.com/9EDP8t6.png"
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='test', password='test123'")
        else:
            print("Test user already exists")

        # Add routes if they don't exist
        if Route.query.count() == 0:
            # Get all difficulty IDs
            difficulties = DifficultyLevel.query.all()
            difficulty_ids = [d.id for d in difficulties]
            
            # Create 50 routes with different difficulties
            route_types = ["boulder", "lead", "top-rope"]
            routes = []
            
            for i in range(1, 51):
                route = Route(
                    difficulty_id=random.choice(difficulty_ids),
                    type=random.choice(route_types)
                )
                routes.append(route)
            
            db.session.add_all(routes)
            db.session.commit()
            print(f"Added {len(routes)} routes")

        # Add completed routes for test user
        user_id = test_user.id
        if CompletedRoute.query.filter_by(user_id=user_id).count() == 0:
            # Get all route IDs
            routes = Route.query.all()
            route_ids = [r.id for r in routes]
            
            # Create 20 completed routes
            completed_routes = []
            for i in range(20):
                # Random date within the last 30 days
                random_days = random.randint(0, 30)
                completion_date = datetime.now() - timedelta(days=random_days)
                
                completed_route = CompletedRoute(
                    user_id=user_id,
                    route_id=random.choice(route_ids),
                    flash=random.choice([True, False]),
                    date=completion_date,
                    image_url="https://i.imgur.com/example.jpg" if random.random() > 0.5 else None
                )
                completed_routes.append(completed_route)
            
            db.session.add_all(completed_routes)
            db.session.commit()
            print(f"Added {len(completed_routes)} completed routes for test user")

        # Add goals for test user
        if Goal.query.filter_by(user_id=user_id).count() == 0:
            goal_types = [
                "Complete a 7A boulder", 
                "Climb 10 routes in one session", 
                "Flash a 6C boulder",
                "Climb outdoors 5 times", 
                "Learn to lead climb"
            ]
            
            goals = []
            for goal_type in goal_types:
                goal = Goal(
                    user_id=user_id,
                    goal_type=goal_type,
                    status=random.choice([True, False])
                )
                goals.append(goal)
            
            db.session.add_all(goals)
            db.session.commit()
            print(f"Added {len(goals)} goals for test user")

        # Add achievements for test user
        if Achievement.query.filter_by(user_id=user_id).count() == 0:
            achievement_names = [
                "First 6A boulder",
                "First flash on a 6B",
                "Climbed 10 days in a row",
                "First outdoor climb",
                "Completed 50 routes"
            ]
            
            achievements = []
            for i, name in enumerate(achievement_names):
                # Achievement dates spread over the last 90 days
                random_days = random.randint(0, 90)
                achievement_date = datetime.now() - timedelta(days=random_days)
                
                achievement = Achievement(
                    user_id=user_id,
                    achievement_name=name,
                    achievement_date=achievement_date
                )
                achievements.append(achievement)
            
            db.session.add_all(achievements)
            db.session.commit()
            print(f"Added {len(achievements)} achievements for test user")

        print("Test data creation complete!")

if __name__ == "__main__":
    create_test_data()