from django.contrib import admin

from server.apps.users.models import BaseUser, BotUser


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    pass


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    pass
