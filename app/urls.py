from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard', views.dashboard, name='dashboard'),
    path('moderator/players', views.player_list, name='player list'),
    path('moderator/add_player', views.add_player, name='add player'),
    path('moderator/signup_locations', views.signup_locations, name='signup locations')
]
