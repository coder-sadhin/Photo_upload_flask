from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, URL
from app.models.user import User


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required')
    ])
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio cannot exceed 500 characters')
    ])
    website = StringField('Website', validators=[
        Optional(),
        URL(message='Please enter a valid URL')
    ])
    location = StringField('Location', validators=[
        Optional(),
        Length(max=100, message='Location cannot exceed 100 characters')
    ])
    gender = SelectField('Gender', choices=[
        ('', 'Prefer not to say'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[Optional()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(min=10, max=20, message='Please enter a valid phone number')
    ])
    is_private = BooleanField('Private Account')
    submit = SubmitField('Update Profile')


class ProfilePictureForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Upload')


class CoverPhotoForm(FlaskForm):
    cover_photo = FileField('Cover Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Upload')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[
        DataRequired(message='Please enter a search term')
    ])
    submit = SubmitField('Search')
