import os
from app import create_app, db
from app.models import *

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Profile': Profile,
        'Post': Post,
        'PostMedia': PostMedia,
        'PostLike': PostLike,
        'PostSave': PostSave,
        'Comment': Comment,
        'CommentLike': CommentLike,
        'Follow': Follow,
        'Notification': Notification,
        'PasswordReset': PasswordReset,
        'Category': Category
    }


@app.cli.command('create-default-files')
def create_default_files():
    """Create default profile and cover images."""
    from PIL import Image
    import os

    profile_pics = app.config['PROFILE_PICS_FOLDER']
    cover_photos = app.config['COVER_PHOTOS_FOLDER']

    os.makedirs(profile_pics, exist_ok=True)
    os.makedirs(cover_photos, exist_ok=True)

    default_profile = os.path.join(profile_pics, 'default_profile.png')
    default_cover = os.path.join(cover_photos, 'default_cover.jpg')

    if not os.path.exists(default_profile):
        img = Image.new('RGB', (400, 400), color=(100, 100, 100))
        img.save(default_profile)

    if not os.path.exists(default_cover):
        img = Image.new('RGB', (1200, 400), color=(100, 100, 100))
        img.save(default_cover)

    print('Default files created!')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
