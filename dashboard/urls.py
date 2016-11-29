from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'(?P<dashboards_id>[0-9]+)/$', views.details, name='detail'),
    url(r'create/$', views.create_dashboard, name='create'),
    url(r'submit/$', views.fellow_submit, name='submitSurvey'),
    url(r'^$', views.home, name='index'),
]