from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^home/$', 'database.views.home'),

    url(r'^upload/$', 'database.views.upload', name='upload'),

    url(r'^select/$', 'database.views.select', name='select'),

    url(r'^norm/$', 'database.views.norm', name='norm'),

    url(r'^graph/$', 'database.views.graph'),

)

