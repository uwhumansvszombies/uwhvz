from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
]
