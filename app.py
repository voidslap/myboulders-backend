from flask import Flask
from flask_cors import CORS
from routes.user_routes import user_routes
from routes.auth_routes import auth_routes
from routes.image_routes import image_routes
from routes.leaderboard_routes import leaderboard_routes
from routes.journal_routes import journal_routes
from config.db_config import db, get_db_uri
from sqlalchemy import inspect
import logging

# Import models
from models.users_model import User
from models.completed_routes_model import CompletedRoute
from models.difficulty_levels_model import DifficultyLevel
from models.routes_model import Route
from models.goals_model import Goal
from models.achievements_model import Achievement

from werkzeug.security import generate_password_hash

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend (React running on port 5173)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Check if database exists and create tables if not
def initialize_database():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        if 'users' not in tables:
            logger.info("Database tables don't exist. Creating all tables...")
            db.create_all()
            logger.info("Database tables created successfully!")
        else:
            logger.info("Database already exists. Skipping creation.")

# Create test user for login testing
def create_test_user():
    with app.app_context():
        # 🔁 Delete old test users with same username or email
        User.query.filter_by(username="admin").delete()
        db.session.commit()

        hashed_password = generate_password_hash("admin123")
        user = User(
            username="admin",
            hashed_password=hashed_password,
            email="admin@example.com",
            profile_image_url="https://via.placeholder.com/150"
        )

        db.session.add(user)
        db.session.commit()
        print("✅ Test user created: admin / admin123")



# Register blueprints
app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(leaderboard_routes, url_prefix='/api/leaderboard')
app.register_blueprint(journal_routes, url_prefix='/api/journal')
app.register_blueprint(image_routes, url_prefix='/api/images')

# Test route
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Run server
if __name__ == '__main__':
    initialize_database()  # Initialize the database first
    create_test_user()     # Then create test users
    app.run(debug=True, port=5000)  # Finally, run the server (only once)