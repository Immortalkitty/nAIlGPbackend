import os
from datetime import timedelta

from dotenv import load_dotenv
from db import db

load_dotenv(".env")

class Config:
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'sqlalchemy'
    SESSION_SQLALCHEMY = db
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'True').lower() == 'true'
    SESSION_USE_SIGNER = os.getenv('SESSION_USE_SIGNER', 'True').lower() == 'true'
    SESSION_SQLALCHEMY_TABLE = os.getenv('SESSION_SQLALCHEMY_TABLE', 'sessions')
    SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'your_session_cookie_name')
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/dev_db')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/prod_db')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
