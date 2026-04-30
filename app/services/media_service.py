from app import db
from app.models.media import Media
from werkzeug.utils import secure_filename
from flask import current_app
import os
import uuid
from PIL import Image


class MediaService:
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}
    ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

    MAX_IMAGE_SIZE = (1920, 1920)
    THUMBNAIL_SIZE = (300, 300)
    QUALITY = 85

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in MediaService.ALLOWED_EXTENSIONS

    @staticmethod
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    @staticmethod
    def is_image(filename):
        return MediaService.get_file_extension(filename) in MediaService.ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def is_video(filename):
        return MediaService.get_file_extension(filename) in MediaService.ALLOWED_VIDEO_EXTENSIONS

    @staticmethod
    def save_media_file(file, folder='post_media'):
        if not file or not file.filename:
            return None

        if not MediaService.allowed_file(file.filename):
            raise ValueError(f'File type not allowed. Allowed types: {", ".join(MediaService.ALLOWED_EXTENSIONS)}')

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        if folder == 'profile_pics':
            folder_path = current_app.config['PROFILE_PICS_FOLDER']
        elif folder == 'cover_photos':
            folder_path = current_app.config['COVER_PHOTOS_FOLDER']
        else:
            folder_path = current_app.config['POST_MEDIA_FOLDER']

        filepath = os.path.join(folder_path, unique_filename)
        file.save(filepath)

        if MediaService.is_image(unique_filename):
            MediaService._optimize_image(filepath)

        return unique_filename

    @staticmethod
    def _optimize_image(filepath):
        try:
            with Image.open(filepath) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                img.thumbnail(MediaService.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                img.save(filepath, optimize=True, quality=MediaService.QUALITY)
        except Exception as e:
            print(f'Error optimizing image: {e}')

    @staticmethod
    def delete_media_file(filename, folder='post_media'):
        if not filename:
            return False

        if folder == 'profile_pics':
            folder_path = current_app.config['PROFILE_PICS_FOLDER']
        elif folder == 'cover_photos':
            folder_path = current_app.config['COVER_PHOTOS_FOLDER']
        else:
            folder_path = current_app.config['POST_MEDIA_FOLDER']

        filepath = os.path.join(folder_path, filename)

        if os.path.exists(filepath):
            os.remove(filepath)
            return True

        return False

    @staticmethod
    def get_media_url(filename, folder='post_media'):
        if not filename:
            return '/static/uploads/default.png'

        return f'/static/uploads/{folder}/{filename}'
