from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.disable_action('delete_selected')
admin.site.register(User, UserAdmin)
