import json
import pytest
import os
import sys
from app import app as flask_app
from models.users_model import User
from config.db_config import db

@pytest.fixture
def app():
    """Create a test app instance with an isolated test database."""
    # Store the original database URI
    original_db_uri = flask_app.config.get('SQLALCHEMY_DATABASE_URI')
    
    # Configure app for testing with in-memory database
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key'
    })

    # Create an application context for the tests
    with flask_app.app_context():
        # Create all tables in the test database
        db.create_all()
        yield flask_app
        # Clean up test database after test
        db.session.remove()
        db.drop_all()
    
    # Restore the original database URI
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri

@pytest.fixture
def client(app):
    """Get a test client for the app."""
    return app.test_client()

@pytest.fixture
def init_database(app):
    """Initialize test database with a test user."""
    with app.app_context():
        # Create a test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            profile_image_url="https://i.imgur.com/test.jpeg"
        )
        test_user.set_password("testpassword")
        db.session.add(test_user)
        db.session.commit()

        yield db  # this is where the testing happens

        # Clean up test data only
        db.session.query(User).filter_by(username="testuser").delete()
        db.session.commit()

def test_register_success(client, app):
    """Test successful user registration."""
    response = client.post('/api/auth/register', 
        json={
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'new@example.com'
        },
        content_type='application/json'
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['username'] == 'newuser'
    assert data['email'] == 'new@example.com'

    # Verify user was actually created in the database
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'

def test_register_duplicate_username(client, init_database):
    """Test registration with duplicate username."""
    # Create an initial user
    response = client.post('/api/auth/register', 
        json={
            'username': 'duplicateuser',
            'password': 'password123',
            'email': 'first@example.com'
        },
        content_type='application/json'
    )
    assert response.status_code == 201

    # Try to create another user with the same username
    response = client.post('/api/auth/register', 
        json={
            'username': 'duplicateuser',
            'password': 'anotherpassword',
            'email': 'second@example.com'
        },
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Username already exists' in data['error']

def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    response = client.post('/api/auth/register', 
        json={
            'username': 'incomplete'
            # Missing password and email
        },
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing required fields' in data['error']

def test_login_success(client, init_database):
    """Test successful login."""
    response = client.post('/api/auth/login', 
        json={
            'username': 'testuser',
            'password': 'testpassword'
        },
        content_type='application/json'
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Login successful'

    # Check that a token cookie was set
    assert 'token' in response.headers.get('Set-Cookie', '')

def test_login_invalid_credentials(client, init_database):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', 
        json={
            'username': 'testuser',
            'password': 'wrongpassword'
        },
        content_type='application/json'
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post('/api/auth/login', 
        json={
            'username': 'testuser'
            # Missing password
        },
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing username or password' in data['error']

def test_check_auth_without_token(client):
    """Test checking auth without a token."""
    response = client.get('/api/auth/check')

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

def test_check_auth_with_token(client, init_database):
    """Test checking auth with a valid token."""
    # First login to get a token
    login_response = client.post('/api/auth/login', 
        json={
            'username': 'testuser',
            'password': 'testpassword'
        },
        content_type='application/json'
    )

    # Extract the token from the cookie
    cookie_header = login_response.headers.get('Set-Cookie')
    assert cookie_header is not None

    # Use the cookie for authentication check
    response = client.get('/api/auth/check', headers={
        'Cookie': cookie_header
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'authenticated' in data
    assert data['authenticated'] is True

def test_logout(client):
    """Test logout functionality."""
    response = client.post('/api/auth/logout')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Logged out'

    # Check that the token cookie was cleared
    cookie_header = response.headers.get('Set-Cookie')
    assert cookie_header is not None
    assert 'token=' in cookie_header

    # Check for any of the possible expiration formats
    cookie_lower = cookie_header.lower()
    assert ('expires=0' in cookie_lower or 
            'expires=thu, 01 jan 1970' in cookie_lower or 
            'max-age=0' in cookie_lower)

def test_me_endpoint_with_token(client, init_database):
    """Test the /me endpoint with a valid token."""
    # First login to get a token
    login_response = client.post('/api/auth/login', 
        json={
            'username': 'testuser',
            'password': 'testpassword'
        },
        content_type='application/json'
    )

    # Extract the token from the cookie
    cookie_header = login_response.headers.get('Set-Cookie')
    assert cookie_header is not None

    # Access the /me endpoint with the token
    response = client.get('/api/auth/me', headers={
        'Cookie': cookie_header
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert 'username' in data
    assert 'email' in data
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'

def test_me_endpoint_without_token(client):
    """Test the /me endpoint without a token."""
    response = client.get('/api/auth/me')

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Authorization token is missing' in data['error']