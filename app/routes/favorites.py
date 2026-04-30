from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.post import Post, PostSave
from app.models.user import User
from app.models.follow import Follow

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)

    saved_posts = PostSave.query.filter_by(user_id=current_user.id).order_by(PostSave.created_at.desc())
    pagination = saved_posts.paginate(page=page, per_page=per_page, error_out=False)

    posts = []
    for save in pagination.items:
        post = save.post
        if not post.is_archived:
            posts.append(post)

    return render_template('favorites/favorites.html',
                           posts=posts,
                           pagination=pagination,
                           title='Saved Posts')


@favorites_bp.route('/post/<int:post_id>/save', methods=['POST'])
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

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'saved': saved,
            'saves_count': post.get_saves_count()
        })

    flash('Post saved!' if saved else 'Post removed from saved.', 'success')
    return redirect(request.referrer or url_for('favorites.favorites'))
