from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.post import Post, PostMedia, PostLike, PostSave
from app.models.category import Category
from app.models.user import User
from app.models.comment import Comment
from app.forms.post_forms import PostForm, CommentForm
from app.services.notification_service import NotificationService
import os
import uuid
from PIL import Image

posts_bp = Blueprint('posts', __name__)


def _resolve_category_from_form():
    new_name = request.form.get('category_new', '').strip()
    raw_id = request.form.get('category_id')
    if new_name:
        return Category.get_or_create(new_name, current_user.id)
    if raw_id not in (None, ''):
        try:
            cid = int(raw_id)
        except (TypeError, ValueError):
            return None
        if cid > 0:
            return Category.query.get(cid)
    return None


@posts_bp.route('/post/create', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content', '').strip()
    visibility = request.form.get('visibility', 'public')
    category = _resolve_category_from_form()

    if not content and not request.files.getlist('media'):
        return jsonify({'success': False, 'message': 'Post must have content or media'}), 400

    post = Post(
        user_id=current_user.id,
        content=content,
        visibility=visibility,
        category_id=category.id if category else None,
    )
    db.session.add(post)
    db.session.flush()

    media_files = request.files.getlist('media')
    for idx, file in enumerate(media_files):
        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"

            is_image = filename.lower().split('.')[-1] in ['jpg', 'jpeg', 'png', 'gif', 'webp']

            if is_image:
                folder = current_app.config['POST_MEDIA_FOLDER']
            else:
                folder = current_app.config['POST_MEDIA_FOLDER']

            filepath = os.path.join(folder, unique_filename)
            file.save(filepath)

            if is_image:
                img = Image.open(filepath)
                img.save(filepath, optimize=True, quality=85)

            media = PostMedia(
                post_id=post.id,
                media_type='image' if is_image else 'video',
                file_path=unique_filename,
                order=idx
            )
            db.session.add(media)

    db.session.commit()

    flash('Your post has been created!', 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'post_id': post.id})

    return redirect(request.referrer or url_for('main.home'))


@posts_bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.visibility != 'public':
        if not current_user.is_authenticated:
            flash('This post is not public.', 'info')
            return redirect(url_for('main.home'))

        if current_user != post.author and not current_user.is_following(post.author.id):
            if post.visibility == 'followers':
                flash('This post is only visible to followers.', 'info')
                return redirect(url_for('main.home'))

    post_author = post.author
    post_profile = post_author.profile

    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).order_by(Comment.created_at.desc()).all()

    return render_template('posts/view_post.html',
                           post=post,
                           comments=comments,
                           title=f'Post by {post_author.username}')


@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash('You can only edit your own posts.', 'danger')
        return redirect(url_for('posts.view_post', post_id=post.id))

    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        visibility = request.form.get('visibility', 'public')
        category = _resolve_category_from_form()

        post.content = content
        post.visibility = visibility
        post.category_id = category.id if category else None
        db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))

    return render_template('posts/edit_post.html', post=post, categories=categories, title='Edit Post')


@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You can only delete your own posts'}), 403

    for media in post.media:
        filepath = os.path.join(current_app.config['POST_MEDIA_FOLDER'], media.file_path)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted.', 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    return redirect(url_for('main.home'))


@posts_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)

    existing_like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        liked = True

        if post.user_id != current_user.id:
            NotificationService.create_notification(
                user_id=post.user_id,
                actor_id=current_user.id,
                notification_type='like',
                post_id=post.id
            )

    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': post.get_likes_count()
    })


@posts_bp.route('/post/<int:post_id>/save', methods=['POST'])
@login_required
def save_post(post_id):
    post = Post.query.get_or_404(post_id)

    existing_save = PostSave.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_save:
        db.session.delete(existing_save)
        db.session.commit()
        saved = False
    else:
        save = PostSave(user_id=current_user.id, post_id=post_id)
        db.session.add(save)
        db.session.commit()
        saved = True

    return jsonify({
        'success': True,
        'saved': saved,
        'saves_count': post.get_saves_count()
    })
