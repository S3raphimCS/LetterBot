from django.contrib import admin

from server.apps.users.models import BaseUser, BotUser


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    pass


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "created_at")
    readonly_fields = ("created_at",)
