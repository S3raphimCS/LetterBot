from typing import List
from server.apps.mailing.models import Scenario, ScenarioStep, ScenarioStepMedia


class ScenarioCheckFieldsService:
    """Класс-сервис для проверки правильности заполнения данных сценария"""

    ERROR_TEXT_MAP = {
        "incorrect_button": "У шага сценария некорректно заполнены данные кнопки",
        "too_many_media": "У шага сценария слишком много медиа. Максимум десять медиа-файлов у одного шага."
    }

    def __init__(self, obj: Scenario):
        self.error_list = []
        self.obj = obj

    def validate(self) -> List[str]:
        for step in self.obj.steps.all():
            self._check_step(step)

        return self.error_list

    def _check_step(self, step: ScenarioStep) -> None:
        if (step.button_text and not step.button_url) or (
                step.button_text and not step.button_url):
            self.error_list.append(self._make_message("incorrect_button"))
        if step.media_files.count() > 10:
            self.error_list.append(self._make_message("too_many_media"))

    def _make_message(self, key, obj_name=None) -> str:
        """Метод подставляющий в сообщение об ошибке название объекта, где была допущена ошибка"""
        return self.ERROR_TEXT_MAP[key].format(obj_name)
