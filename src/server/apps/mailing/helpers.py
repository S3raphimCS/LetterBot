from django.conf import settings
from django.core.exceptions import ValidationError


def validate_photo_size(value):
    if value.size > settings.MAX_PHOTO_SIZE:
        raise ValidationError('Загруженное фото больше 10 Мб')
