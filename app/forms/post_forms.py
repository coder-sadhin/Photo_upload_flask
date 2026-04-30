from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError


class PostForm(FlaskForm):
    content = TextAreaField('What\'s on your mind?', validators=[
        Optional(),
        Length(max=2200, message='Post cannot exceed 2200 characters')
    ])
    visibility = SelectField('Visibility', choices=[
        ('public', 'Public'),
        ('followers', 'Followers Only'),
        ('private', 'Private')
    ], default='public')
    submit = SubmitField('Post')


class MediaUploadForm(FlaskForm):
    media = MultipleFileField('Upload Media', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'], 'Only image and video files are allowed!')
    ])
    submit = SubmitField('Upload')


class CommentForm(FlaskForm):
    content = StringField('Add a comment...', validators=[
        DataRequired(message='Please enter a comment'),
        Length(max=500, message='Comment cannot exceed 500 characters')
    ])
    submit = SubmitField('Post')


class ReplyForm(FlaskForm):
    content = StringField('Write a reply...', validators=[
        DataRequired(message='Please enter a reply'),
        Length(max=500, message='Reply cannot exceed 500 characters')
    ])
    submit = SubmitField('Reply')
