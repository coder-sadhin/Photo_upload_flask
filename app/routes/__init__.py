from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.posts import posts_bp
from app.routes.comments import comments_bp
from app.routes.favorites import favorites_bp
from app.routes.notifications import notifications_bp
from app.routes.main import main_bp


def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/')
    app.register_blueprint(posts_bp, url_prefix='/')
    app.register_blueprint(comments_bp, url_prefix='/')
    app.register_blueprint(favorites_bp, url_prefix='/')
    app.register_blueprint(notifications_bp, url_prefix='/')
    app.register_blueprint(main_bp)
