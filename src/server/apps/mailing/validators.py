import os

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_size(value):
    """Валидатор для проверки размера файла"""

    ext = os.path.splitext(value.name)[1]

    if ext in ['.jpg', '.jpeg', '.png']:
        if value.size > settings.MAX_PHOTO_SIZE:
            raise ValidationError('Загруженное изображение больше 10 Мб')

    if ext in ['mp4', 'mov', 'avi', 'hevc']:
        if value.size > settings.MAX_VIDEO_SIZE:
            raise ValidationError("Загружаемый файл больше 50 Мб")


def validate_url(value):
    """Валидатор для того, чтобы проверить, что ссылка начинается с https://"""
    if not value.startswith('https'):
        raise ValidationError('Ссылка должна начинаться с https://')
