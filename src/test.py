from telebot.types import InputMediaPhoto
from server.bot.main import bot
from pathlib import Path
from server.apps.mailing.models import ScenarioStep
from django.conf import settings


def test():
    step = ScenarioStep.objects.last()
    photos = step.media_files.all()

    print("============================================")
    media_group = [InputMediaPhoto(Path(i.photo.path).open(mode='rb'), caption=step.text) for i in photos]

    telegram_id = 1118806718

    bot.send_media_group(
        chat_id=telegram_id,
        media=media_group
    )
    bot.send_message(
        chat_id=telegram_id,
        text=step.text,
    )
