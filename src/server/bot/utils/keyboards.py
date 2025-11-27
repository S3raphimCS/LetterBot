from typing import Dict, List

from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class KeyboardConstructor:
    """Класс формирования кнопок и клавиатур."""

    def __init__(
            self,
            row_width: int = 1,
            resize_keyboard: bool = True,
            one_time_keyboard: bool = True,
    ):
        """Инициализация параметров."""
        self.row_width = row_width
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard

    def create_inline_keyboard(self, data: Dict[str, str]) -> InlineKeyboardMarkup:
        """Метод формирования инлайн-клавиатуры."""
        inline_buttons = self._create_inline_buttons(data)
        keyboard = InlineKeyboardMarkup(row_width=self.row_width)
        keyboard.add(*inline_buttons)
        return keyboard

    def create_mixed_keyboard(
            self,
            callback_data: Dict[str, str] = None,
            url_data: Dict[str, str] = None,
    ) -> InlineKeyboardMarkup:
        """Метод формирования смешанной клавиатуры."""
        inline_buttons = self._create_inline_buttons(callback_data) if callback_data else []
        url_buttons = self._create_url_buttons(url_data) if url_data else []

        keyboard = InlineKeyboardMarkup(row_width=self.row_width)
        keyboard.add(*inline_buttons)
        keyboard.add(*url_buttons)
        return keyboard

    def create_reply_keyboard(self, data: List[dict]) -> ReplyKeyboardMarkup:
        """Метод формирования реплай-клавиатуры."""
        reply_buttons = self._create_reply_buttons(data)
        keyboard = ReplyKeyboardMarkup(
            row_width=self.row_width,
            resize_keyboard=self.resize_keyboard,
            one_time_keyboard=self.one_time_keyboard,
        )
        keyboard.add(*reply_buttons)
        return keyboard

    @staticmethod
    def _create_inline_buttons(data: Dict[str, str]) -> List[InlineKeyboardButton]:
        """Метод формирования кнопок для инлайн-клавиатуры."""
        return [InlineKeyboardButton(text=key, callback_data=value) for key, value in data.items()]

    @staticmethod
    def _create_reply_buttons(data: List[dict]) -> List[KeyboardButton]:
        """Метод формирования кнопок для реплай-клавиатуры."""
        return [KeyboardButton(**params) for params in data]

    @staticmethod
    def _create_url_buttons(data: Dict[str, str]) -> List[InlineKeyboardButton]:
        """Метод формирования кнопок для инлайн-клавиатуры."""
        return [InlineKeyboardButton(text=key, url=value) for key, value in data.items()]
