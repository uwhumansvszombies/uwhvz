from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import GameCreateView, GameDetailsView, PlayerCreateView, PlayerDetailsView
from app.accounts import UserCreateView, UserDetailsView


urlpatterns = [
    # path('', views.index, name='index'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('dashboard/', views.dashboard, name='dashboard'),
    url(r'^users/$', UserCreateView.as_view(), name="create"),
    url(r'^users/(?P<username>[\w._+-]+)/$', UserDetailsView.as_view(), name="details"),
    url(r'^games/$', GameCreateView.as_view(), name="create"),
    url(r'^games/(?P<pk>[^/]+)/$', GameDetailsView.as_view(), name="details"),
    url(r'^players/$', PlayerCreateView.as_view(), name="create"),
    url(r'^players/(?P<pk>[^/]+)/$', PlayerDetailsView.as_view(), name="details"),
]


urlpatterns = format_suffix_patterns(urlpatterns)
