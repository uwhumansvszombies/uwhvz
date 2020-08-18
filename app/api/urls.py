from django.urls import path, include

from app.api.views import api_view

urlpatterns = [
    path('account_info/', api_view.account_info),
    path('stun_tag/', api_view.stun_tag),
    path('supply_code/', api_view.claim_supply_code),
    path('view_tags/', api_view.view_tags),
    path('auth/login/', api_view.view_login),
    path('auth/logout/', api_view.view_logout)
]