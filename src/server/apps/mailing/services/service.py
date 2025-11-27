from typing import List
from server.apps.mailing.models import Scenario, ScenarioStep, ScenarioStepPhoto


class ScenarioCheckFieldsService:
    """Класс-сервис для проверки правильности заполнения данных сценария"""

    ERROR_TEXT_MAP = {
        "incorrect_button": "У шага сценария некорректно заполнены данные кнопки"
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

    def _make_message(self, key, obj_name=None) -> str:
        """Метод подставляющий в сообщение об ошибке название объекта, где была допущена ошибка"""
        return self.ERROR_TEXT_MAP[key].format(obj_name)
