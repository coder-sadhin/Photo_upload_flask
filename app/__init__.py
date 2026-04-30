import importlib
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def _apply_sqlite_schema_patches():
    """Add new tables/columns for existing SQLite DBs (create_all does not alter tables)."""
    from sqlalchemy import inspect, text

    eng = db.engine
    if eng.dialect.name != 'sqlite':
        return
    insp = inspect(eng)
    if not insp.has_table('categories'):
        from app.models.category import Category

        Category.__table__.create(eng, checkfirst=True)
        insp = inspect(eng)
    if not insp.has_table('posts'):
        return
    cols = {c['name'] for c in insp.get_columns('posts')}
    if 'category_id' not in cols:
        with eng.begin() as conn:
            conn.execute(text('ALTER TABLE posts ADD COLUMN category_id INTEGER'))


def create_app(config_name='default'):
    from config import config

    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(base_dir)

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static'),
    )
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from app.routes import register_routes
    register_routes(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    with app.app_context():
        importlib.import_module('app.models')
        db.create_all()
        _apply_sqlite_schema_patches()

    @app.cli.command('init-db')
    def init_db_command():
        """Create database tables (use when not using auto-create in DEBUG)."""
        importlib.import_module('app.models')
        db.create_all()
        _apply_sqlite_schema_patches()
        print('Database initialized successfully!')

    return app
