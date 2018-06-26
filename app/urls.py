from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/<uuid:signup_token>', views.UserSignupView.as_view(), name='user_signup'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/report_tag', views.ReportTagView.as_view(), name='report_tag'),
    path('dashboard/players', views.PlayerListView.as_view(), name='player_list'),
    path('dashboard/add_player', views.AddPlayerView.as_view(), name='add_player'),
    path('dashboard/signup_locations', views.SignupLocationsView.as_view(), name='signup_locations'),
    path('dashboard/signup', views.GameSignupView.as_view(), name='game_signup'),
    path('signup/<uuid:signup_token>', views.signup, name='signup')
]
