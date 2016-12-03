from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^submit/(?P<hash_value>[\w]+)/$',
        views.fellow_submit, name='submitSurvey'),
    url(r'^dashboards/(?P<dashboard_id>[0-9]+)/$',
        views.details, name='detail'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^$', views.home, name='index'),
]
