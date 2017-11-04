from django.conf.urls import url, include
import django.contrib.auth.urls

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
]
