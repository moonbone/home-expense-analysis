__author__ = 'maord'

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^missing$', views.missing, name='missing'),
    url(r'^details$', views.details, name='details'),
    url(r'^$', views.report, name='report'),
]
