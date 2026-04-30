from app.forms.auth_forms import (
    RegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm
)

from app.forms.profile_forms import (
    ProfileForm,
    ProfilePictureForm,
    CoverPhotoForm,
    SearchForm
)

from app.forms.post_forms import (
    PostForm,
    MediaUploadForm,
    CommentForm,
    ReplyForm
)

__all__ = [
    'RegistrationForm',
    'LoginForm',
    'ForgotPasswordForm',
    'ResetPasswordForm',
    'ChangePasswordForm',
    'ProfileForm',
    'ProfilePictureForm',
    'CoverPhotoForm',
    'SearchForm',
    'PostForm',
    'MediaUploadForm',
    'CommentForm',
    'ReplyForm'
]
