from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from server.apps.mailing.enums import SendingStatus
from server.apps.mailing.models import Mailing, MailingLog, MailingMedia, ScenarioMailingLog, Scenario, ScenarioStep, \
    ScenarioStepMedia, UserScenarioMailing
from nested_admin.nested import NestedStackedInline, NestedModelAdmin
from server.apps.mailing.services.service import ScenarioCheckFieldsService
from server.apps.mailing import help_texts
from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
)
from django.contrib.auth.models import Group


models_to_unregister = [
    Group,
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
]
for model in models_to_unregister:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


class MailingMediaInline(admin.StackedInline):
    model = MailingMedia
    extra = 0
    ordering = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": ("mailing", "media",),
                "description": help_texts.MAILING_MEDIA_HELP_TEXT
            },
        ),
    )


class ScenarioStepMediaInline(NestedStackedInline):
    model = ScenarioStepMedia
    extra = 0
    ordering = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": ("scenario", "media",),
                "description": help_texts.SCENARIO_STEP_MEDIA_HELP_TEXT
            },
        ),
    )


class ScenarioStepInline(NestedStackedInline):
    model = ScenarioStep
    extra = 1
    ordering = ("id",)
    inlines = [ScenarioStepMediaInline]

    help_texts = help_texts.SCENARIO_STEP_HELP_TEXTS

    def get_formset(self, request, obj, **kwargs):
        kwargs.update(
            {"help_texts": self.help_texts},
        )
        return super().get_formset(request, obj, **kwargs)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    inlines = [MailingMediaInline]
    list_display = ["title", "is_processed", "successful_sent_count"]
    readonly_fields = ("is_processed", "successful_sent_count")
    fields_help_texts = help_texts.MAILING_FIELDS_HELP_TEXT

    def successful_sent_count(self, obj):
        return obj.logs.filter(sending_status=SendingStatus.SUCCESS).count()

    successful_sent_count.short_description = "Успешно отправленных"

    fieldsets = (
        (
            None,
            {
                "fields": tuple(),
                "description": help_texts.MAILING_HELP_TEXT
            },
        ),
        (
            "Наполнение письма",
            {
                "fields": ("title", "text", "button_text", "button_link")
            }
        ),
        (
            "Если запланированная рассылка",
            {
                "fields": ("time_start",)
            },
        ),
        (
            "Если немедленная рассылка",
            {
                "fields": ("is_instant", )
            }
        ),
        (
            "Состояние рассылки",
            {
                "fields": ("ready_to_send", "is_processed", "successful_sent_count"),
            },
        ),
    )

    def get_form(self, *args, **kwargs):
        kwargs.update(
            {'help_texts': self.fields_help_texts},
        )
        return super().get_form(*args, **kwargs)


@admin.register(Scenario)
class ScenarioAdmin(NestedModelAdmin):
    inlines = [ScenarioStepInline]
    list_display = ["title", "steps", "trigger_delay_hours", "is_active", "received"]
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
        obj.refresh_from_db()
        errors = ScenarioCheckFieldsService(obj).validate()
        if errors:
            for message in errors:
                self.message_user(request, message, messages.ERROR, fail_silently=False)
            obj.is_active = False
            obj.save(update_fields=("is_active",))
            return False

        return True
