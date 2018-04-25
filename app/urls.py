from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/report_tag', views.report_tag, name='report tag'),
    path('dashboard/players', views.player_list, name='player list'),
    path('dashboard/add_player', views.add_player, name='add player'),
    path('dashboard/signup_locations', views.signup_locations, name='signup locations'),
    path('dashboard/signup/<uuid:signup_token>', views.signup, name='signup')
]
