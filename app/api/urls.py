from django.urls import path, include

from app.api.views import api_view

urlpatterns = [
    path('account_info/', api_view.account_info),
    path('auth/login/', api_view.view_login),
    path('auth/logout/', api_view.view_logout)
]