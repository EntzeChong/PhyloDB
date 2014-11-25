from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'^home/$', 'database.views.home'),
    url(r'^upload/$', 'database.views.upload', name='upload'),
    url(r'^select/$', 'database.views.select', name='select'),
    url(r'^graph/$', 'database.views.graph', name='graph'),

    url(r'^getProjectTree/$', 'database.trees.getProjectTree', name='getProjectTree'),
    url(r'^getSampleCatTree/$', 'database.trees.getSampleCatTree', name='getSampleCatTree'),
    url(r'^getSampleQuantTree/$', 'database.trees.getSampleQuantTree', name='getSampleQuantTree'),

    url(r'^getCatGraphData', 'database.trees.getCatGraphData', name='getCatGraphData'),
    url(r'^getQuantGraphData', 'database.trees.getQuantGraphData', name='getQuantGraphData'),

    url(r'^getTaxaTree/$', 'database.trees.getTaxaTree', name='getTaxaTree'),

)


