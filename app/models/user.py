from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.follow import Follow
from app.models.post import Post, PostLike, PostSave


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship(
        'Notification',
        foreign_keys='Notification.user_id',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_followers_count(self):
        return Follow.query.filter_by(followed_id=self.id).count()

    def get_following_count(self):
        return Follow.query.filter_by(follower_id=self.id).count()

    def get_posts_count(self):
        return Post.query.filter_by(user_id=self.id).count()

    def is_following(self, user_id):
        return Follow.query.filter_by(follower_id=self.id, followed_id=user_id).first() is not None

    def is_followed_by(self, user_id):
        """True if user_id follows this user (they are a follower of self)."""
        return Follow.query.filter_by(follower_id=user_id, followed_id=self.id).first() is not None

    def has_liked_post(self, post_id):
        return PostLike.query.filter_by(user_id=self.id, post_id=post_id).first() is not None

    def has_saved_post(self, post_id):
        return PostSave.query.filter_by(user_id=self.id, post_id=post_id).first() is not None

    def __repr__(self):
        return f'<User {self.username}>'
