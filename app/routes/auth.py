from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models.user import User
from app.models.profile import Profile
from app.models.notification import Notification
from app.forms.auth_forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm
from app.services.notification_service import NotificationService
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        profile = Profile(
            user_id=user.id,
            full_name=form.full_name.data
        )
        db.session.add(profile)
        db.session.commit()

        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return render_template('auth/login.html', title='Login', form=form)

            login_user(user, remember=form.remember_me.data)

            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')

            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            token = secrets.token_urlsafe(32)
            from app.models.password_reset import PasswordReset
            password_reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(password_reset)
            db.session.commit()

            flash(f'Password reset link sent to {user.email}. (Token: {token})', 'info')
        else:
            flash('If an account exists with this email, a reset link has been sent.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    from app.models.password_reset import PasswordReset
    password_reset = PasswordReset.query.filter_by(token=token).first()

    if not password_reset or not password_reset.is_valid():
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.get(password_reset.user_id)
        user.set_password(form.password.data)
        password_reset.is_used = True
        db.session.commit()

        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form, token=token)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html', title='Change Password', form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()

        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('users.profile', username=current_user.username))

    return render_template('auth/change_password.html', title='Change Password', form=form)
