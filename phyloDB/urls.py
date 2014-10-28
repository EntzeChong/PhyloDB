from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^home/$', 'database.views.home'),

    url(r'^upload/$', 'database.views.upload', name='upload'),

    url(r'^select/$', 'database.views.select', name='select'),

    url(r'^graph/$', 'database.views.graph', name='graph'),

    url(r'^getProjectTree/$', 'database.views.getProjectTree', name='getProjectTree'),

    url(r'^getTaxaTree/$', 'database.views.getTaxaTree', name='getTaxaTree'),

)

