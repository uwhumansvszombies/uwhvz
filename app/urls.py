from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/<uuid:signup_token>', views.UserSignupView.as_view(), name='user_signup'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/report_tag', views.ReportTagView.as_view(), name='report_tag'),
    path('dashboard/signup', views.GameSignupView.as_view(), name='game_signup'),
    path('dashboard/claim_supply_code', views.ClaimSupplyCodeView.as_view(), name='claim_supply_code'),
    path('signup/<uuid:signup_token>', views.signup, name='signup'),
    path('dashboard/moderator/add_player', views.AddPlayerView.as_view(), name='add_player'),
    path('dashboard/moderator/generate_supply_code', views.GenerateSupplyCodeView.as_view(), name='generate_supply_codes'),
    path('dashboard/moderator/player_list', views.PlayerListView.as_view(), name='player_list'),
    path('dashboard/moderator/signup_locations', views.SignupLocationsView.as_view(), name='signup_locations'),
]
