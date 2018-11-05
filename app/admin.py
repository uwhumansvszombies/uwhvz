from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import *


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'role', 'faction__name')
    list_display = ('get_full_name', 'game', 'code', 'role', 'faction', 'score', 'active')
    ordering = ('-game__created_at', 'user__first_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.admin_order_field = 'user__first_name'
    get_full_name.short_description = 'Name'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_display = ('get_full_name', 'character_name', 'game', 'active')
    ordering = ('-game__created_at', 'user__first_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.admin_order_field = 'user__first_name'
    get_full_name.short_description = 'Name'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Spectator)
class SpectatorAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_display = ('get_full_name', 'game', 'active')
    ordering = ('-game__created_at', 'user__first_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.admin_order_field = 'user__first_name'
    get_full_name.short_description = 'Name'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SupplyCode)
class SupplyCodeAdmin(admin.ModelAdmin):
    search_fields = ('game', 'code')
    list_display = ('code', 'game', 'active')
    ordering = ('-game__created_at', 'code')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('initiator__user__first_name', 'initiator__user__last_name', 'receiver__user__first_name', 'receiver__user__last_name')
    list_display = ('tagged_at', 'get_initiator_name', 'get_receiver_name', 'active')
    ordering = ('-tagged_at',)

    def get_initiator_name(self, obj):
        return obj.initiator.user.get_full_name()

    get_initiator_name.admin_order_field = 'initiator__user__first_name'
    get_initiator_name.short_description = 'Initiator Name'

    def get_receiver_name(self, obj):
        return obj.receiver.user.get_full_name()

    get_receiver_name.admin_order_field = 'receiver__user__first_name'
    get_receiver_name.short_description = 'Receiver Name'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SignupLocation)
class SignupLocationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'game')
    list_display = ('name', 'game')
    ordering = ('-game__created_at',)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SignupInvite)
class SignupInviteAdmin(admin.ModelAdmin):
    search_fields = ('game', 'email', 'signup_location__name')
    list_display = ('email', 'game', 'signup_location')
    ordering = ('-game__created_at',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form_template = 'admin/add_user_form.html'

    search_fields = ('first_name', 'last_name', 'email')
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Modifier)
class ModifierAdmin(admin.ModelAdmin):
    pass


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    pass


admin.site.disable_action('delete_selected')
