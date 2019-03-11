from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    # Landing
    path("", views.IndexView.as_view(), name='index'),

    # Signups/Account pages
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(
        html_email_template_name="registration/password_reset_email_html.html"
    )),
    path("accounts/", include('django.contrib.auth.urls')),
    path("accounts/signup/<uuid:signup_invite>", views.UserSignupView.as_view(), name='user_signup'),
    path("accounts/signup/", views.UnrestrictedUserSignupView.as_view(), name='unrestricted_user_signup'),
    path("dashboard/game-signup", views.GameSignupView.as_view(), name='game_signup'),
    path("dashboard/volunteer/signup-players", views.SignupPlayersView.as_view(), name='signup_players'),
    path("signup/<uuid:signup_invite>", views.signup, name='signup'),
    path("game-signup/<uuid:signup_invite>", views.TokenRequiredGameSignupView.as_view(), name='token_game_signup'),

    # Default dashboard pages
    path("dashboard", views.DashboardView.as_view(), name='dashboard'),

    # Player/Game pages
    path("dashboard/player", views.PlayerInfoView.as_view(), name='player_info'),
    path("dashboard/claim-supply-code", views.ClaimSupplyCodeView.as_view(), name='claim_supply_code'),
    path("dashboard/report-tag", views.ReportTagView.as_view(), name='report_tag'),
    path("dashboard/player-list", views.PlayerListView.as_view(), name='player_list'),
    path("dashboard/message-players", views.MessagePlayersView.as_view(), name='message_players'),
    path("dashboard/zombie-tree", views.ZombieTreeView.as_view(), name='zombie_tree'),

    # Moderator pages
    path("dashboard/moderator/generate-supply-codes", views.GenerateSupplyCodesView.as_view(),
         name='generate_supply_codes'),
    path("dashboard/moderator/manage-game", views.ManageGameView.as_view(), name='manage_game'),
    path("dashboard/moderator/kill-unsupplied-humans", views.KillUnsuppliedHumansView.as_view(),
         name='kill_unsupplied_humans'),
    path("dashboard/moderator/manage-oz", views.ManageOZView.as_view(), name='manage_oz'),
    path("dashboard/moderator/manage-players", views.ManagePlayersView.as_view(), name='manage_players'),
]
