from django.urls import path
from .views import my_view


urlpatterns = [
    path('', my_view, name='index'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('dashboard/', views.dashboard, name='dashboard'),
]
