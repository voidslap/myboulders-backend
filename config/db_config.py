import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

class Config:
    # 🔐 Fallback används om .env-nyckel saknas
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///myboulders.db")

def get_db_uri():
    return Config.SQLALCHEMY_DATABASE_URI
