import os
from datetime import datetime

DB_VERSION = '1.0'
APP_NAME = 'SocialMedia'
APP_VERSION = '1.0.0'

class DatabaseConfig:
    @staticmethod
    def get_engine_uri(db_type='sqlite', **kwargs):
        if db_type == 'postgresql':
            return f"postgresql://{kwargs.get('user')}:{kwargs.get('password')}@{kwargs.get('host')}:{kwargs.get('port')}/{kwargs.get('database')}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{kwargs.get('user')}:{kwargs.get('password')}@{kwargs.get('host')}:{kwargs.get('port')}/{kwargs.get('database')}"
        else:
            return kwargs.get('sqlite_path', 'sqlite:///social_media.db')
