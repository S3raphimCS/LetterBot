from loguru import logger
import requests
from rest_framework import status

from server import settings


class TelegramBotWebhook:
    """Класс установки вебхука для бота Telegram."""

    def __init__(self, token: str, url: str):
        self.token = token
        self.url = url

    @property
    def set_webhook_url(self):
        return 'https://api.telegram.org/bot{token}/setWebHook?url={domain}/{url}/'.format(
            token=self.token,
            domain=settings.APP_URL,
            url=self.url,
        )

    @property
    def delete_webhook_url(self):
        return 'https://api.telegram.org/bot{token}/deleteWebHook'.format(
            token=self.token,
        )

    def run(self):
        try:
            response = requests.get(self.delete_webhook_url)
            status_code = response.status_code

            if status_code != status.HTTP_200_OK:
                logger.error(
                    'Ошибка удаления вебхука для бота: {exc}\n{trace}'.format(
                        exc=status_code,
                        trace=response.raise_for_status(),
                    ),
                )
                raise Exception

            response = requests.get(self.set_webhook_url)
            status_code = response.status_code

            if status_code != status.HTTP_200_OK:
                logger.error(
                    'Ошибка установки вебхука для бота: {exc}\n{trace}'.format(
                        exc=status_code,
                        trace=response.raise_for_status(),
                    ),
                )
                raise Exception
            logger.info('Вебхук установлен')
        except Exception as exc:
            logger.error('Ошибка запуска бота: {exc}'.format(exc=exc))
            