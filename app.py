from flask import Flask
from flask_cors import CORS
from routes.user_routes import user_routes
from routes.auth_routes import auth_routes
from routes.leaderboard import leaderboard_bp
from routes.journal_routes import journal_routes
from config.db_config import db, get_db_uri

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(leaderboard_bp, url_prefix='/api')
app.register_blueprint(journal_routes, url_prefix='/api/journal')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, port=5000)