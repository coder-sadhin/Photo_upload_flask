from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.models.profile import Profile
from app.models.post import Post, PostLike, PostSave
from app.models.follow import Follow
from app.models.notification import Notification
from app.forms.profile_forms import ProfileForm, ProfilePictureForm, CoverPhotoForm, SearchForm
from app.services.notification_service import NotificationService
import os
import uuid
from PIL import Image

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    profile = user.profile

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)

    posts_query = Post.query.filter_by(user_id=user.id, is_archived=False).order_by(Post.created_at.desc())

    if user != current_user:
        if profile.is_private:
            if not current_user.is_authenticated or not current_user.is_following(user.id):
                flash('This account is private.', 'info')
                return render_template('users/private_profile.html', user=user, profile=profile)
            posts_query = posts_query.filter(Post.visibility.in_(['public', 'followers']))
        else:
            posts_query = posts_query.filter(Post.visibility.in_(['public', 'followers']))

    posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)

    is_following = current_user.is_following(user.id) if current_user.is_authenticated else False
    is_followed_by = current_user.is_followed_by(user.id) if current_user.is_authenticated else False

    return render_template('users/profile.html',
                           user=user,
                           profile=profile,
                           posts=posts,
                           is_following=is_following,
                           is_followed_by=is_followed_by,
                           title=f'{user.username} - Profile')


@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user.profile)

    if form.validate_on_submit():
        current_user.profile.full_name = form.full_name.data
        current_user.profile.bio = form.bio.data
        current_user.profile.website = form.website.data
        current_user.profile.location = form.location.data
        current_user.profile.gender = form.gender.data
        current_user.profile.date_of_birth = form.date_of_birth.data
        current_user.profile.phone = form.phone.data
        current_user.profile.is_private = form.is_private.data

        db.session.commit()

        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('users.profile', username=current_user.username))

    return render_template('users/edit_profile.html',
                           form=form,
                           title='Edit Profile')


@users_bp.route('/profile/picture', methods=['GET', 'POST'])
@login_required
def update_profile_picture():
    form = ProfilePictureForm()

    if form.validate_on_submit():
        file = form.profile_picture.data
        if file:
            file.stream.seek(0)
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(current_app.config['PROFILE_PICS_FOLDER'], unique_filename)

            img = Image.open(file.stream)
            ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
            if ext in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(filepath, optimize=True, quality=85)

            if current_user.profile.profile_picture != 'default_profile.png':
                old_picture = os.path.join(current_app.config['PROFILE_PICS_FOLDER'], current_user.profile.profile_picture)
                if os.path.exists(old_picture):
                    os.remove(old_picture)

            current_user.profile.profile_picture = unique_filename
            db.session.commit()

            flash('Profile picture updated successfully!', 'success')

    return redirect(url_for('users.edit_profile'))


@users_bp.route('/profile/cover', methods=['GET', 'POST'])
@login_required
def update_cover_photo():
    form = CoverPhotoForm()

    if form.validate_on_submit():
        file = form.cover_photo.data
        if file:
            file.stream.seek(0)
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(current_app.config['COVER_PHOTOS_FOLDER'], unique_filename)

            img = Image.open(file.stream)
            ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
            if ext in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(filepath, optimize=True, quality=85)

            if current_user.profile.cover_photo != 'default_cover.jpg':
                old_cover = os.path.join(current_app.config['COVER_PHOTOS_FOLDER'], current_user.profile.cover_photo)
                if os.path.exists(old_cover):
                    os.remove(old_cover)

            current_user.profile.cover_photo = unique_filename
            db.session.commit()

            flash('Cover photo updated successfully!', 'success')

    return redirect(url_for('users.edit_profile'))


@users_bp.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)

    pagination = Follow.query.filter_by(followed_id=user.id).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('users/followers.html',
                           user=user,
                           followers=pagination.items,
                           pagination=pagination,
                           title=f'{user.username} - Followers')


@users_bp.route('/following/<username>')
def following(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)

    pagination = Follow.query.filter_by(follower_id=user.id).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('users/following.html',
                           user=user,
                           following=pagination.items,
                           pagination=pagination,
                           title=f'{user.username} - Following')


@users_bp.route('/follow/<user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)

    if user == current_user:
        return jsonify({'success': False, 'message': 'You cannot follow yourself'}), 400

    if current_user.is_following(user.id):
        follow_record = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()
        db.session.delete(follow_record)
        db.session.commit()

        NotificationService.create_notification(
            user_id=user.id,
            actor_id=current_user.id,
            notification_type='unfollow'
        )

        return jsonify({'success': True, 'following': False, 'message': 'Unfollowed successfully'})

    else:
        follow_record = Follow(follower_id=current_user.id, followed_id=user.id)
        db.session.add(follow_record)
        db.session.commit()

        NotificationService.create_notification(
            user_id=user.id,
            actor_id=current_user.id,
            notification_type='follow'
        )

        return jsonify({'success': True, 'following': True, 'message': 'Following successfully'})


@users_bp.route('/suggested-users')
@login_required
def suggested_users():
    limit = current_app.config.get('SUGGESTED_USERS_LIMIT', 5)

    following_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=current_user.id).all()]
    following_ids.append(current_user.id)

    suggested = User.query.filter(~User.id.in_(following_ids)).limit(limit).all()

    return render_template('users/suggested.html', users=suggested, title='Suggested Users')


@users_bp.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '')

    if not query:
        return render_template('search.html', title='Search', users=[], posts=[])

    users = User.query.filter(
        (User.username.ilike(f'%{query}%')) |
        (User.profile.has(full_name=query))
    ).limit(20).all()

    return render_template('search.html', users=users, query=query, title='Search Results')
