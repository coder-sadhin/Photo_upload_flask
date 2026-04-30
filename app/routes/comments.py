from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.comment import Comment, CommentLike
from app.models.notification import Notification
from app.forms.post_forms import CommentForm, ReplyForm
from app.services.notification_service import NotificationService

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()

    if not content:
        return jsonify({'success': False, 'message': 'Comment cannot be empty'}), 400

    comment = Comment(
        user_id=current_user.id,
        post_id=post_id,
        content=content
    )
    db.session.add(comment)
    db.session.commit()

    if post.user_id != current_user.id:
        NotificationService.create_notification(
            user_id=post.user_id,
            actor_id=current_user.id,
            notification_type='comment',
            post_id=post.id,
            comment_id=comment.id
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'user': {
                    'username': current_user.username,
                    'profile_picture': current_user.profile.profile_picture
                },
                'created_at': comment.created_at.strftime('%b %d, %Y at %I:%M %p'),
                'likes_count': 0
            }
        })

    flash('Comment added!', 'success')
    return redirect(request.referrer or url_for('posts.view_post', post_id=post_id))


@comments_bp.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def add_reply(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content', '').strip()

    if not content:
        return jsonify({'success': False, 'message': 'Reply cannot be empty'}), 400

    reply = Comment(
        user_id=current_user.id,
        post_id=comment.post_id,
        parent_id=comment.id,
        content=content
    )
    db.session.add(reply)
    db.session.commit()

    if comment.user_id != current_user.id:
        NotificationService.create_notification(
            user_id=comment.user_id,
            actor_id=current_user.id,
            notification_type='reply',
            post_id=comment.post_id,
            comment_id=comment.id
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'reply': {
                'id': reply.id,
                'content': reply.content,
                'user': {
                    'username': current_user.username,
                    'profile_picture': current_user.profile.profile_picture
                },
                'created_at': reply.created_at.strftime('%b %d, %Y at %I:%M %p'),
                'likes_count': 0
            }
        })

    flash('Reply added!', 'success')
    return redirect(request.referrer or url_for('posts.view_post', post_id=comment.post_id))


@comments_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    existing_like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.session.add(like)
        db.session.commit()
        liked = True

        if comment.user_id != current_user.id:
            NotificationService.create_notification(
                user_id=comment.user_id,
                actor_id=current_user.id,
                notification_type='comment_like',
                comment_id=comment.id
            )

    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': comment.get_likes_count()
    })


@comments_bp.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You can only edit your own comments'}), 403

    content = request.form.get('content', '').strip()

    if not content:
        return jsonify({'success': False, 'message': 'Comment cannot be empty'}), 400

    comment.content = content
    comment.is_edited = True
    db.session.commit()

    return jsonify({
        'success': True,
        'content': comment.content,
        'is_edited': True
    })


@comments_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You can only delete your own comments'}), 403

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('Comment deleted.', 'success')
    return redirect(url_for('posts.view_post', post_id=post_id))
