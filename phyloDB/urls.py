from django.conf.urls import *


urlpatterns = patterns('',

    url(r'^home/$', 'database.views.home', name='home'),
    url(r'^upload/$', 'database.views.upload', name='upload'),
    url(r'^select/$', 'database.views.select', name='select'),
    url(r'^alpha_graphs/$', 'database.views.alpha_diversity', name='alpha'),
    url(r'^beta-graphs/$', 'database.views.beta_diversity', name='beta'),

    url(r'^cookie/$', 'database.views.cookie', name='cookie'),

    url(r'^getProjectTree/$', 'database.trees.getProjectTree', name='getProjectTree'),
    url(r'^getProjectTreeChildren/$', 'database.trees.getProjectTreeChildren', name='getProjectTreeChildren'),

    url(r'^getSampleCatTree/$', 'database.trees.getSampleCatTree', name='getSampleCatTree'),
    url(r'^getSampleCatTreeChildren/$', 'database.trees.getSampleCatTreeChildren', name='getSampleCatTreeChildren'),

    url(r'^getSampleQuantTree/$', 'database.trees.getSampleQuantTree', name='getSampleQuantTree'),

    url(r'^getTaxaTree/$', 'database.trees.getTaxaTree', name='getTaxaTree'),

    url(r'^getCatAlphaData', 'database.trees.getCatAlphaData', name='getCatAlphaData'),
    url(r'^getQuantAlphaData', 'database.trees.getQuantAlphaData', name='getQuantAlphaData'),
    url(r'^getCatBetaData', 'database.trees.getCatBetaData', name='getCatBetaData'),
    url(r'^getQuantBetaData', 'database.trees.getQuantBetaData', name='getQuantBetaData'),

)


