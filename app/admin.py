from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from app.models import Player, SupplyCode, Game, Tag, User, SignupLocation, SignupInvite, Modifier, Faction


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'role', 'faction__name')
    list_display = ('get_full_name', 'game', 'code', 'role', 'faction', 'score', 'active')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.admin_order_field = 'user__first_name'
    get_full_name.short_description = 'Name'

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
    search_fields = ('initiator__user__first_name', 'initiator__user__last_name', 'receiver__user__first_name', 'receiver__user__last_name')

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SignupLocation)
class SignupLocationAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SignupInvite)
class SignupInviteAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form_template = 'admin/add_user_form.html'

    search_fields = ('first_name', 'last_name', 'email')
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
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
