import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'social_media.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'webm', 'mov'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PROFILE_PICS_FOLDER = os.path.join(UPLOAD_FOLDER, 'profile_pics')
    COVER_PHOTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'cover_photos')
    POST_MEDIA_FOLDER = os.path.join(UPLOAD_FOLDER, 'post_media')

    for folder in [UPLOAD_FOLDER, PROFILE_PICS_FOLDER, COVER_PHOTOS_FOLDER, POST_MEDIA_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    POSTS_PER_PAGE = 10
    NOTIFICATIONS_PER_PAGE = 20
    SUGGESTED_USERS_LIMIT = 5


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
