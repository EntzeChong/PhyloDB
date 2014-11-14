from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'^home/$', 'database.views.home'),
    url(r'^upload/$', 'database.views.upload', name='upload'),
    url(r'^select/$', 'database.views.select', name='select'),
    url(r'^graph/$', 'database.views.graph', name='graph'),

    url(r'^getProjectTree/$', 'database.trees.getProjectTree', name='getProjectTree'),
    url(r'^getSelectedSamples/$', 'database.trees.getSelectedSamples', name='getSelectedSamples'),
    url(r'^getSampleTree/$', 'database.trees.getSampleTree', name='getSampleTree'),
    url(r'^getTaxaTree/$', 'database.trees.getTaxaTree', name='getTaxaTree'),



)


