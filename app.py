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

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Check if database exists and create if it doesn't
def initialize_database():
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check for existence of key tables (adjust based on your models)
        tables = inspector.get_table_names()
        if 'users' not in tables:
            logger.info("Database tables don't exist. Creating all tables...")
            db.create_all()
            logger.info("Database tables created successfully!")
        else:
            logger.info("Database already exists. Skipping creation.")

# Initialize the database
initialize_database()

# Register blueprints
app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(leaderboard_routes, url_prefix='/api/leaderboard')
app.register_blueprint(journal_routes, url_prefix='/api/journal')
app.register_blueprint(image_routes, url_prefix='/api/images')  

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, port=5000)