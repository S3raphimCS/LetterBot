from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from server.apps.mailing.models import Mailing, MailingLog, MailingPhoto, ScenarioMailingLog, Scenario, ScenarioStep, \
    ScenarioStepPhoto, UserScenarioMailing
from nested_admin.nested import NestedStackedInline, NestedModelAdmin
from server.apps.mailing.services.service import ScenarioCheckFieldsService
from server.apps.mailing import help_texts


class MailingPhotoInline(admin.StackedInline):
    model = MailingPhoto
    extra = 0
    ordering = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": ("mailing", "photo",),
                "description": help_texts.MAILING_PHOTO_HELP_TEXT
            },
        ),
    )


class ScenarioStepPhotoInline(NestedStackedInline):
    model = ScenarioStepPhoto
    extra = 0
    ordering = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": ("scenario", "photo",),
                "description": help_texts.SCENARIO_STEP_PHOTO_HELP_TEXT
            },
        ),
    )


class ScenarioStepInline(NestedStackedInline):
    model = ScenarioStep
    extra = 1
    ordering = ("id",)
    inlines = [ScenarioStepPhotoInline]

    help_texts = help_texts.SCENARIO_STEP_HELP_TEXTS

    def get_formset(self, request, obj, **kwargs):
        kwargs.update(
            {"help_texts": self.help_texts},
        )
        return super().get_formset(request, obj, **kwargs)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    inlines = [MailingPhotoInline]


@admin.register(Scenario)
class ScenarioAdmin(NestedModelAdmin):
    inlines = [ScenarioStepInline]
    list_display = ["title", "steps", "trigger_delay_hours", "received"]
    help_text = help_texts.SCENARIO_HELP_TEXT

    def steps(self, obj):
        return obj.steps.count()

    def received(self, obj):
        return obj.steps.last().users.count()

    steps.short_description = "Шагов"
    received.short_description = "Пользователей полностью получили рассылку"

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "trigger_delay_hours", "is_active"),
                "description": help_texts.SCENARIO_HELP_TEXT
            },
        ),
    )

    def response_add(self, request, obj, post_url_continue=None):
        if obj.is_active and not self._is_valid(request, obj):
            return redirect(reverse("admin:mailing_scenario_change", args=[obj.id]))

        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        """Метод для валидации заполненных данных модели сценария и отображения ошибок"""
        if obj.is_active and not self._is_valid(request, obj):
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def _is_valid(self, request, obj):
        # TODO Добавить проверку на то, что не более 10 фото к одному сообщению
        obj.refresh_from_db()
        errors = ScenarioCheckFieldsService(obj).validate()
        if errors:
            for message in errors:
                self.message_user(request, message, messages.ERROR, fail_silently=False)
            obj.is_active = False
            obj.save(update_fields=("is_active",))
            return False

        return True
