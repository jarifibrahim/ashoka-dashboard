from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^consultant/(?P<hash_value>[\w]+)/$',
        views.consultant_submit, name='consultant_survey'),
    url(r'^fellow/(?P<hash_value>[\w]+)/$',
        views.fellow_submit, name='fellow_survey'),
    url(r'^dashboards/(?P<dashboard_id>[0-9]+)/$',
        views.dashboard_overview, name='dashboard_overview'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^urls/$', views.show_urls, name='show_urls'),
    url(r'^update/$', views.update_value, name='update'),
    url(r'^teams/(?P<team_id>[0-9]+)/$', views.team_detail,
        name='team_display'),
    url(r'email/', views.send_email, name='send_email'),
    url(r'warnings/', views.show_warnings, name='show_warnings'),
    url(r'members/$', views.get_members, name='get_members'),
    url(r'^$', views.home, name='index'),
]
