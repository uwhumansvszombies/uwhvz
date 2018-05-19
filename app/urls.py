from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/<uuid:signup_token>', views.user_signup, name='user_signup'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/report_tag', views.report_tag, name='report_tag'),
    path('dashboard/players', views.player_list, name='player_list'),
    path('dashboard/add_player', views.add_player, name='add_player'),
    path('dashboard/signup_locations', views.signup_locations, name='signup_locations'),
    path('dashboard/signup', views.game_signup, name='game_signup'),
    path('signup/<uuid:signup_token>', views.signup, name='signup')
]
