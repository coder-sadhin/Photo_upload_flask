from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('NOTIFICATIONS_PER_PAGE', 20)

    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc())
    pagination = notifications.paginate(page=page, per_page=per_page, error_out=False)

    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()

    return render_template('notifications/notifications.html',
                           notifications=pagination.items,
                           pagination=pagination,
                           unread_count=unread_count,
                           title='Notifications')


@notifications_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)

    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify({'success': True})


@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.notifications'))


@notifications_bp.route('/notifications/count')
@login_required
def count():
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()

    return jsonify({'count': unread_count})


@notifications_bp.route('/notification/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)

    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    db.session.delete(notification)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('Notification deleted.', 'success')
    return redirect(url_for('notifications.notifications'))
