from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import Player, SupplyCode, Game, Tag, User


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(SupplyCode)
class SupplyCodeAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
