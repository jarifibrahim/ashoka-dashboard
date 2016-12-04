from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^consultant/(?P<hash_value>[\w]+)/$',
        views.consultant_submit, name='consultant_survey'),
    url(r'^fellow/(?P<hash_value>[\w]+)/$',
        views.fellow_submit, name='fellow_survey'),
    url(r'^dashboards/(?P<dashboard_id>[0-9]+)/$',
        views.details, name='detail'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^urls/$', views.show_urls, name='show_urls'),
    url(r'^$', views.home, name='index'),
]
