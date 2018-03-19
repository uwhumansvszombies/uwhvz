from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import Player, SupplyCode, Game, Tag, User, SignupLocation


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SupplyCode)
class SupplyCodeAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SignupLocation)
class SignupLocationAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.disable_action('delete_selected')
