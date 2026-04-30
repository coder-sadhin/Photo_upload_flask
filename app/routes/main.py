from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.post import Post, PostLike, PostSave
from app.models.category import Category
from app.models.user import User
from app.models.follow import Follow
from app.models.notification import Notification

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    return render_template('main/landing.html', title='Welcome')


@main_bp.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)

    following_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.id).all()]
    following_ids.append(current_user.id)

    timeline_posts = Post.query.filter(
        Post.user_id.in_(following_ids),
        Post.is_archived == False,
        Post.visibility.in_(['public', 'followers'])
    ).order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    explore_posts = Post.query.filter(
        Post.user_id.notin_(following_ids),
        Post.is_archived == False,
        Post.visibility == 'public'
    ).order_by(Post.created_at.desc()).limit(10).all()

    categories = Category.query.order_by(Category.name).all()

    return render_template('main/home.html',
                           posts=timeline_posts.items,
                           pagination=timeline_posts,
                           explore_posts=explore_posts,
                           categories=categories,
                           title='Home')


@main_bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    category_slug = request.args.get('category', '', type=str).strip().lower()

    posts_q = Post.query.filter_by(is_archived=False, visibility='public')
    active_category = ''

    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            posts_q = posts_q.filter(Post.category_id == cat.id)
            active_category = category_slug
        else:
            posts_q = posts_q.filter(Post.id == -1)

    posts_q = posts_q.order_by(Post.created_at.desc())
    pagination = posts_q.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.order_by(Category.name).all()

    return render_template('main/explore.html',
                           posts=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           active_category=active_category,
                           title='Explore')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    profile = user.profile

    total_posts = Post.query.filter_by(user_id=user.id, is_archived=False).count()
    total_followers = Follow.query.filter_by(followed_id=user.id).count()
    total_following = Follow.query.filter_by(follower_id=user.id).count()
    total_saves = PostSave.query.filter_by(user_id=user.id).count()
    total_likes = PostLike.query.filter_by(user_id=user.id).count()
    unread_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).count()

    recent_posts = Post.query.filter_by(user_id=user.id, is_archived=False).order_by(Post.created_at.desc()).limit(5).all()
    recent_notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()

    posts_liked = Post.query.join(PostLike).filter(PostLike.user_id == user.id).order_by(PostLike.created_at.desc()).limit(5).all()

    suggested_users = []
    following_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=user.id).all()]
    following_ids.append(user.id)

    if len(following_ids) < 10:
        suggested_users = User.query.filter(~User.id.in_(following_ids)).limit(5).all()

    categories = Category.query.order_by(Category.name).all()

    return render_template('main/dashboard.html',
                           user=user,
                           profile=profile,
                           total_posts=total_posts,
                           total_followers=total_followers,
                           total_following=total_following,
                           total_saves=total_saves,
                           total_likes=total_likes,
                           unread_notifications=unread_notifications,
                           recent_posts=recent_posts,
                           recent_notifications=recent_notifications,
                           posts_liked=posts_liked,
                           suggested_users=suggested_users,
                           categories=categories,
                           title='Dashboard')


@main_bp.route('/settings')
@login_required
def settings():
    return render_template('main/settings.html', title='Settings')
