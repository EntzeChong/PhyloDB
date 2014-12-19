from django.conf.urls import *


urlpatterns = patterns('',

    url(r'^home/$', 'database.views.home'),
    url(r'^upload/$', 'database.views.upload', name='upload'),
    url(r'^select/$', 'database.views.select', name='select'),
    url(r'^graph/$', 'database.views.graph', name='graph'),

    url(r'^getProjectTree/$', 'database.trees.getProjectTree', name='getProjectTree'),
    url(r'^getProjectTreeChildren/$', 'database.trees.getProjectTreeChildren', name='getProjectTreeChildren'),

    url(r'^getSampleCatTree/$', 'database.trees.getSampleCatTree', name='getSampleCatTree'),
    #url(r'^getSampleCatTreeChildren/$', 'database.trees.getSampleCatTreeChildren', name='getSampleCatTreeChildren'),
    url(r'^getSampleQuantTree/$', 'database.trees.getSampleQuantTree', name='getSampleQuantTree'),
    url(r'^getTaxaTree/$', 'database.trees.getTaxaTree', name='getTaxaTree'),
    #url(r'^getTaxaTreeChildren/$', 'database.trees.getTaxaTreeChildren', name='getTaxaTreeChildren'),


    url(r'^getCatGraphData', 'database.trees.getCatGraphData', name='getCatGraphData'),
    url(r'^getQuantGraphData', 'database.trees.getQuantGraphData', name='getQuantGraphData'),

    url(r'^ANOVA/$', 'database.trees.ANOVA', name='ANOVA'),

    #url(r'^abundRegr/$', 'database.trees.abundRegr', name='abundRegr'),
    #url(r'^richRegr/$', 'database.trees.richRegr', name='richRegr'),
)


