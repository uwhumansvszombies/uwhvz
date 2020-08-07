from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import *
from app.models.tag import TagType
from app.views.forms import UserCreationForm, UserChangeForm

def mark_oz_bulk(ModelAdmin, request, queryset):
    queryset.update(is_oz=True)
mark_oz_bulk.short_description = "Make OZ"

def remove_oz_bulk(ModelAdmin, request, queryset):
    queryset.update(is_oz=False)
remove_oz_bulk.short_description = "Remove OZ"

def get_legacy(self, instance):
    return instance.user.legacy_points
get_legacy.short_description = 'Legacy Points'

def set_stun(ModelAdmin, request, queryset):
    queryset.update(type=TagType.STUN)
set_stun.short_description = "Set Tag to Stun"

def set_kill(ModelAdmin, request, queryset):
    queryset.update(type=TagType.KILL)
set_kill.short_description = "Set Tag to Kill"

def set_inactive(ModelAdmin, request, queryset):
    queryset.update(active=False)
set_inactive.short_description = "Inactivate Tag"

def set_active(ModelAdmin, request, queryset):
    queryset.update(active=True)
set_active.short_description = "Activate Tag"

class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    fieldsets = (
        (('User'), {'fields': ('email','is_staff', 'legacy_points')}),
        (('Permissions'), {'fields': ('is_active','is_staff')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'get_legacy')



@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'role', 'faction__name', 'in_oz_pool')
    list_display = ('get_full_name', 'game', 'code', 'role', 'faction', 'score', 'active', 'in_oz_pool','is_oz')
    ordering = ('-game__created_at', 'user__first_name')
    actions = [mark_oz_bulk,remove_oz_bulk]

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.admin_order_field = 'user__first_name'
    get_full_name.short_description = 'Name'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
  
@admin.register(Legacy)
class LegacyAdmin(admin.ModelAdmin):
    search_fields = ('user', 'time','value')
    list_display = ('user', 'time', 'value')
    ordering = ('time', 'user')
    
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
    search_fields = ('game', 'code', 'value')
    list_display = ('code', 'game', 'active', 'value')
    ordering = ('-game__created_at', 'code')

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    search_fields = ('game', 'buyer', 'time','cost')
    list_display = ('buyer', 'game', 'time', 'active', 'cost')
    ordering = ('-game__created_at', 'time')

    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('initiator__user__first_name', 'initiator__user__last_name', 'receiver__user__first_name', 'receiver__user__last_name')
    list_display = ('__str__', 'type','get_initiator_name', 'get_receiver_name', 'tagged_at', 'game', 'active')
    ordering = ('-tagged_at',)
    actions = [set_kill,set_stun,remove_tag,set_inactive,set_active]

    def get_initiator_name(self, obj):
        return obj.initiator.user.get_full_name()

    get_initiator_name.admin_order_field = 'initiator__user__first_name'
    get_initiator_name.short_description = 'Initiator Name'

    def get_receiver_name(self, obj):
        return obj.receiver.user.get_full_name()

    get_receiver_name.admin_order_field = 'receiver__user__first_name'
    get_receiver_name.short_description = 'Receiver Name'
    
    def game(self, obj):
        return obj.initiator.game

    game.admin_order_field = 'initiator__game'
    game.short_description = 'Game'

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(SignupLocation)
class SignupLocationAdmin(admin.ModelAdmin):
    search_fields = ('name', 'game')
    list_display = ('name', 'game')
    ordering = ('-game__created_at',)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SignupInvite)
class SignupInviteAdmin(admin.ModelAdmin):
    search_fields = ('email', 'game__name', 'signup_location__name')
    list_display = ('email', 'game', 'signup_location', 'participant_role', 'used_at')
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
        return request.user.is_superuser


@admin.register(Modifier)
class ModifierAdmin(admin.ModelAdmin):
    pass


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    pass


#admin.site.disable_action('delete_selected')
