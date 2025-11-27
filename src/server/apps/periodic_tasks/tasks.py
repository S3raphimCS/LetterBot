import time
from datetime import timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from loguru import logger
from telebot import apihelper, types
from telebot.types import InputMediaPhoto
from telebot.types import WebAppInfo
from server import celery_app
from server.apps.mailing.models import Mailing, MailingLog, Scenario, ScenarioStep
from server.apps.mailing.enums import SendingStatus
from server.apps.users.models import BotUser
from server.bot.main import bot
from server.bot.utils.keyboards import KeyboardConstructor

User = get_user_model()


@celery_app.app.task
def send_user_step(telegram_id: int, step: ScenarioStep) -> None:
    """Задача отправки шага сценария пользователю."""
    photos = step.photos.all()

    if step.delay_seconds:
        time.sleep(step.delay_seconds)

    data = {}
    if step.button_text and step.button_url:
        data = data.update({step.button_text: step.button_url})

    keyboard = KeyboardConstructor().create_mixed_keyboard(url_data=data)

    if photos:
        # TODO Возможно не будет работать Path и надо сделать просто open
        # TODO Сделать ограничение на одновременное количество фото >= 2 и кнопки
        media_group = [InputMediaPhoto(Path(i.photo.path).open(mode='rb'), caption=step.text) for i in photos]
        bot.send_media_group(
            chat_id=telegram_id,
            media=media_group

        )
    else:
        bot.send_message(
            chat_id=telegram_id,
            text=step.text,
            reply_markup=keyboard
        )


@celery_app.app.task
def check_scenario_dispatcher() -> None:
    """Задача поиска пользователей, подходящих для рассылки и создания задачи рассылки"""

    now = timezone.now()
    scenarios = Scenario.objects.prefetch_related("steps").all()

    for scenario in scenarios:
        cutoff_time = now - timedelta(hours=scenario.trigger_delay_hours)

        users_to_process = BotUser.objects.filter(
            created_at__lte=cutoff_time
        ).exclude(
            scenarios__scenario=scenario
        )

        if not users_to_process.exists():
            continue

        steps = scenario.steps.all().order_by("id")

        if not steps:
            continue

        for user in users_to_process:
            try:
                for step in steps:
                    send_user_step.delay(user.telegram_id, step)

            except Exception as err:
                logger.error(f"Возникла ошибка при поиске пользователей для сценария: {err}")


@celery_app.app.task
def send_instant_mailing() -> None:
    """Задача отправки рассылки со статусом ready_to_send=True и is_instant=True."""
    mailings = Mailing.objects.filter(ready_to_send=True, is_processed=False, is_instant=True)
    for mailing in mailings:
        mailing.is_processed = True
        mailing.save(update_fields=["is_processed"])
        subs = BotUser.objects.filter(is_active=True)

        for sub in subs:
            try:
                keyboard = {

                }

                if mailing.button_link and mailing.button_text:
                    keyboard.update({})

                # TODO Можно ли так делать
                if mailing.images:
                    # Отправка
                    pass
                else:
                    # Отправка без изображений
                    pass


                if mailing.button_link and mailing.button_link:
                    kb_builder = KeyboardBuilder()
                    buttons_list = [
                        types.InlineKeyboardButton("Заказать в чат-боте",
                                                   callback_data=f"menu:track:to_bot:{mailing.id}"),
                        types.InlineKeyboardButton(f"{mailing.button_text}", url=mailing.button_link),
                    ]
                    kb_builder.add_rows(buttons_list, row_width=1)
                    keyboard = kb_builder.build()
                    if mailing.image:
                        photo = Path(mailing.image.path)
                        bot.send_photo(
                            chat_id=sub.telegram_id,
                            photo=photo.open(mode="rb"),
                            caption=mailing.body,
                            reply_markup=keyboard
                        )
                    else:
                        bot.send_message(
                            chat_id=sub.telegram_id,
                            text=mailing.body,
                            reply_markup=keyboard
                        )
                else:
                    buttons_list = [
                        types.InlineKeyboardButton("Заказать в чат-боте",
                                                   callback_data=f"menu:track:to_bot:{mailing.id}"),
                    ]
                    kb_builder = KeyboardBuilder()
                    kb_builder.add_rows(buttons_list, row_width=1)
                    keyboard = kb_builder.build()
                    if mailing.image:
                        photo = Path(mailing.image.path)
                        bot.send_photo(
                            chat_id=sub.telegram_id,
                            photo=photo.open(mode="rb"),
                            caption=mailing.body,
                            reply_markup=keyboard
                        )
                    else:
                        bot.send_message(
                            chat_id=sub.telegram_id,
                            text=mailing.body,
                            reply_markup=keyboard
                        )
            except apihelper.ApiTelegramException as e:
                if e.error_code == 403 and "bot was blocked by the user" in e.description:
                    if sub.bot == mailing.bot:
                        sub.is_active = False
                        sub.save(update_fields=["is_active"])
                        logger.info(f"Пользователь {sub.telegram_id} заблокировал бота.")
                elif e.error_code == 400 and "chat not found" in e.description:
                    if sub.bot == mailing.bot:
                        sub.is_active = False
                        sub.save(update_fields=["is_active"])
                        logger.warning(f"Чат {sub.telegram_id} не найден. Деактивируем.")
                elif e.error_code == 403 and "user is deactivated" in e.description:
                    sub.is_active = False
                    sub.save(update_fields=["is_active"])
                    logger.info(f"Пользователь {sub.telegram_id} деактивирован.")
                else:
                    logger.error(f"Неожиданная ошибка Telegram API для пользователя {sub.telegram_id}: {e}")
                if sub.bot == mailing.bot:
                    MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=e,
                                              sending_status=SendingStatus.ERROR)
            except Exception as err:
                if sub.bot == mailing.bot:
                    MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=err,
                                              sending_status=SendingStatus.ERROR)
                    logger.error(f"Ошибка при отправке рассылки: {err}")
            else:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, sending_status=SendingStatus.SUCCESS)
                logger.info("Отправка рассылки успешно завершена")

        mailing.is_processed = True
        mailing.save(update_fields=["is_processed"])

