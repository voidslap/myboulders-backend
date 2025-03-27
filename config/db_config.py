import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

def get_db_uri():
    return os.getenv('DATABASE_URL')