from datetime import timedelta
from pathlib import Path
import time

from django.contrib.auth import get_user_model
from django.utils import timezone
from loguru import logger
from telebot import apihelper
from telebot.types import InputMediaPhoto, InputMediaVideo

from server import celery_app
from server.apps.mailing.enums import SendingStatus
from server.apps.mailing.models import (
    Mailing,
    MailingLog,
    Scenario,
    ScenarioStep,
    UserScenarioMailing,
)
from server.apps.periodic_tasks.helpers import except_telegram_exception, media_is_video
from server.apps.users.models import BotUser
from server.bot.main import bot
from server.bot.utils.keyboards import KeyboardConstructor


User = get_user_model()


@celery_app.app.task
def send_user_step(telegram_id: int, step_id: int) -> None:
    """Задача отправки шага сценария пользователю."""
    step = ScenarioStep.objects.get(id=step_id)
    media_files = step.media_files.all()
    user = BotUser.objects.get(telegram_id=telegram_id)
    if UserScenarioMailing.objects.filter(user=user, scenario=step).exists():
        return
    UserScenarioMailing.objects.create(user=user, scenario=step)

    if step.delay_seconds:
        time.sleep(step.delay_seconds)

    data = {}
    is_button_used = False
    if step.button_text and step.button_url:
        is_button_used = True

    if is_button_used:
        data = {step.button_text: step.button_url}

    keyboard = KeyboardConstructor().create_mixed_keyboard(url_data=data)

    try:
        if media_files.exists():
            if media_files.count() > 1:
                # Поскольку в тг есть ограничение, что с медиа группой нельзя отправить кнопки,
                # то отправляем двумя сообщениями, если есть кнопка
                media_group = []
                for media_instance in media_files.all():
                    if media_is_video(media_instance.media.path):
                        media_group.append(
                            InputMediaVideo(
                                Path(media_instance.media.path).open(mode='rb'),
                                caption=step.text
                            )
                        )
                    else:
                        media_group.append(
                            InputMediaPhoto(
                                Path(media_instance.media.path).open(mode='rb'),
                                caption=step.text
                            )
                        )
                bot.send_media_group(
                    chat_id=telegram_id,
                    media=media_group
                )
                bot.send_message(
                    chat_id=telegram_id,
                    text=step.text,
                    reply_markup=keyboard
                )

            else:
                media_path = media_files.first().media.path
                if media_is_video(media_path):
                    bot.send_video(
                        chat_id=telegram_id,
                        video=Path(media_path).open(mode='rb'),
                        caption=step.text,
                        reply_markup=keyboard
                    )
                else:
                    bot.send_photo(
                        chat_id=telegram_id,
                        photo=Path(media_path).open(mode='rb'),
                        caption=step.text,
                        reply_markup=keyboard
                    )
        else:
            bot.send_message(
                chat_id=telegram_id,
                text=step.text,
                reply_markup=keyboard
            )
    except apihelper.ApiTelegramException as e:
        log_message = except_telegram_exception(e, user)
        logger.error(log_message)
    except Exception as err:
        logger.error(f"Возникла ошибка при отправке пользователю {telegram_id} шага сценария {step.id}: {err}")
    else:
        logger.success(f"Шаг сценария {step.id} успешно отправлен пользователю {telegram_id}")


@celery_app.app.task
def check_scenario_dispatcher() -> None:
    """Задача поиска пользователей, подходящих для рассылки и создания задачи рассылки"""

    now = timezone.now()
    scenarios = Scenario.objects.filter(is_active=True).prefetch_related("steps").all()

    for scenario in scenarios:
        try:
            cutoff_time = now - timedelta(hours=scenario.trigger_delay_hours)

            steps = scenario.steps.all().order_by("id")

            if not steps.exists():
                continue

            for step in steps:
                users_to_process = BotUser.objects.filter(
                    created_at__lte=cutoff_time,
                    is_active=True
                ).exclude(
                    scenarios__scenario__scenario=scenario
                )

                if not users_to_process.exists():
                    continue

                for user in users_to_process:
                    send_user_step.delay(user.telegram_id, step.id)

        except Exception as err:
            logger.exception(f"Возникла ошибка при поиске пользователей для сценария: {err}")


@celery_app.app.task
def send_instant_mailing() -> None:
    """Задача отправки рассылки со статусом ready_to_send=True и is_instant=True."""
    mailings = Mailing.objects.filter(ready_to_send=True, is_processed=False, is_instant=True)
    for mailing in mailings:
        mailing.is_processed = True
        mailing.save(update_fields=["is_processed"])
        is_button_used = False
        data = {}
        if mailing.button_text and mailing.button_link:
            is_button_used = True
        if is_button_used:
            data = {mailing.button_text: mailing.button_link}
        keyboard = KeyboardConstructor().create_mixed_keyboard(url_data=data)
        subs = BotUser.objects.filter(is_active=True)
        media_files = mailing.media_files.all()

        for sub in subs:
            try:
                if media_files.exists():
                    if media_files.count() > 1:
                        media_group = []
                        for media_instance in media_files.all():
                            if media_is_video(media_instance.media.path):
                                media_group.append(
                                    InputMediaVideo(
                                        Path(media_instance.media.path).open(mode='rb'),
                                        caption=mailing.text
                                    )
                                )
                            else:
                                media_group.append(
                                    InputMediaPhoto(
                                        Path(media_instance.media.path).open(mode='rb'),
                                        caption=mailing.text
                                    )
                                )
                        bot.send_media_group(
                            chat_id=sub.telegram_id,
                            media=media_group
                        )
                        bot.send_message(
                            chat_id=sub.telegram_id,
                            text=mailing.text,
                            reply_markup=keyboard
                        )
                    else:
                        media_path = media_files.first().media.path
                        if media_is_video(media_path):
                            bot.send_video(
                                chat_id=sub.telegram_id,
                                video=Path(media_path).open(mode='rb'),
                                caption=mailing.text,
                                reply_markup=keyboard
                            )
                        else:
                            bot.send_photo(
                                chat_id=sub.telegram_id,
                                photo=Path(media_path).open(mode='rb'),
                                caption=mailing.text,
                                reply_markup=keyboard
                            )
                else:
                    bot.send_message(
                        chat_id=sub.telegram_id,
                        text=mailing.text,
                        reply_markup=keyboard
                    )
            except apihelper.ApiTelegramException as e:
                log_message = except_telegram_exception(e, sub)
                logger.error(log_message)
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=e,
                                          sending_status=SendingStatus.ERROR)
            except Exception as err:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=err,
                                          sending_status=SendingStatus.ERROR)
                logger.error(f"Ошибка при отправке рассылки: {err}")
            else:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, sending_status=SendingStatus.SUCCESS)
                logger.info("Отправка рассылки успешно завершена")


@celery_app.app.task
def send_timed_mailing() -> None:
    """Задача отправки рассылки со статусом ready_to_send=True и is_instant=True."""
    now = timezone.now()
    mailings = Mailing.objects.filter(ready_to_send=True, is_processed=False, is_instant=False, time_start__lte=now)
    for mailing in mailings:
        mailing.is_processed = True
        mailing.save(update_fields=["is_processed"])
        is_button_used = False
        data = {}
        if mailing.button_text and mailing.button_link:
            is_button_used = True
        if is_button_used:
            data = {mailing.button_text: mailing.button_link}
        keyboard = KeyboardConstructor().create_mixed_keyboard(url_data=data)
        subs = BotUser.objects.filter(is_active=True)
        media_files = mailing.media_files.all()
        for sub in subs:
            try:
                if media_files.exists():
                    if media_files.count() > 1:
                        media_group = []
                        for media_instance in media_files:
                            if media_is_video(media_instance.media.path):
                                media_group.append(
                                    InputMediaVideo(
                                        Path(media_instance.media.path).open(mode='rb'),
                                        caption=mailing.text
                                    )
                                )
                            else:
                                media_group.append(
                                    InputMediaPhoto(
                                        Path(media_instance.media.path).open(mode='rb'),
                                        caption=mailing.text
                                    )
                                )
                        bot.send_media_group(
                            chat_id=sub.telegram_id,
                            media=media_group
                        )
                        bot.send_message(
                            chat_id=sub.telegram_id,
                            text=mailing.text,
                            reply_markup=keyboard
                        )
                    else:
                        media_path = media_files.first().media.path
                        if media_is_video(media_path):
                            bot.send_video(
                                chat_id=sub.telegram_id,
                                video=Path(media_path).open(mode='rb'),
                                caption=mailing.text,
                                reply_markup=keyboard
                            )
                        else:
                            bot.send_photo(
                                chat_id=sub.telegram_id,
                                photo=Path(media_path).open(mode='rb'),
                                caption=mailing.text,
                                reply_markup=keyboard
                            )
                else:
                    bot.send_message(
                        chat_id=sub.telegram_id,
                        text=mailing.text,
                        reply_markup=keyboard
                    )
            except apihelper.ApiTelegramException as e:
                log_message = except_telegram_exception(e, sub)
                logger.error(log_message)
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=e,
                                          sending_status=SendingStatus.ERROR)
            except Exception as err:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, error=err,
                                          sending_status=SendingStatus.ERROR)
                logger.error(f"Ошибка при отправке рассылки: {err}")
            else:
                MailingLog.objects.create(mail=mailing, user_id=sub.telegram_id, sending_status=SendingStatus.SUCCESS)
                logger.info("Отправка рассылки успешно завершена")


@celery_app.app.task
def broadcast_video_note(file_id, admin_id):
    users = BotUser.objects.filter(is_active=True)

    sent_count = 0

    for user in users:
        try:
            bot.send_video_note(
                user.telegram_id,
                file_id
            )
            sent_count += 1
            time.sleep(0.05)

        except Exception as err:
            logger.error(f"Возникла ошибка при отправке кружка: {err}")

    bot.send_message(
        chat_id=admin_id,
        text=f"✅ Кружок получили {sent_count} человек"
    )


@celery_app.app.task
def broadcast_voice_message(file_id, admin_id):
    users = BotUser.objects.filter(is_active=True)

    sent_count = 0

    for user in users:
        try:
            bot.send_voice(
                user.telegram_id,
                file_id
            )
            sent_count += 1
            time.sleep(0.05)

        except Exception as err:
            logger.error(f"Возникла ошибка при отправке кружка: {err}")

    bot.send_message(
        chat_id=admin_id,
        text=f"✅ Голосовое сообщение получили {sent_count} человек"
    )
