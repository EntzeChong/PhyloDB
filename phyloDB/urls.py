from django.conf.urls import *


urlpatterns = patterns('',

    url(r'^home/$', 'database.views.home', name='home'),
    url(r'^upload/$', 'database.views.upload', name='upload'),
    url(r'^select/$', 'database.views.select', name='select'),
    url(r'^taxa/$', 'database.views.taxa', name='taxa'),
    url(r'^alpha_graphs/$', 'database.views.alpha_diversity', name='alpha'),
    url(r'^beta-graphs/$', 'database.views.beta_diversity', name='beta'),

    url(r'^saveCookie/$', 'database.views.saveCookie', name='saveCookie'),
    url(r'^getCookie/$', 'database.views.getCookie', name='getCookie'),

    url(r'^getProjectTree/$', 'database.trees.getProjectTree', name='getProjectTree'),
    url(r'^getProjectTreeChildren/$', 'database.trees.getProjectTreeChildren', name='getProjectTreeChildren'),

    url(r'^getSampleCatTree/$', 'database.trees.getSampleCatTree', name='getSampleCatTree'),
    url(r'^getSampleCatTreeChildren/$', 'database.trees.getSampleCatTreeChildren', name='getSampleCatTreeChildren'),

    url(r'^getSampleQuantTree/$', 'database.trees.getSampleQuantTree', name='getSampleQuantTree'),
    url(r'^getSampleQuantTreeChildren/$', 'database.trees.getSampleQuantTreeChildren', name='getSampleQuantTreeChildren'),

    url(r'^getTaxaTree/$', 'database.trees.getTaxaTree', name='getTaxaTree'),
    url(r'^getTaxaTreeChildren/$', 'database.trees.getTaxaTreeChildren', name='getTaxaTreeChildren'),

    url(r'^getCatAlphaData', 'database.alpha_graphs.getCatAlphaData', name='getCatAlphaData'),
    url(r'^getQuantAlphaData', 'database.alpha_graphs.getQuantAlphaData', name='getQuantAlphaData'),
    url(r'^getCatBetaData', 'database.beta_graphs.getCatBetaData', name='getCatBetaData'),
    url(r'^getQuantBetaData', 'database.beta_graphs.getQuantBetaData', name='getQuantBetaData'),

    url(r'^instructions', 'database.views.instructions', name='instructions'),
    url(r'^project_file', 'database.views.project_file', name='project_file'),
    url(r'^sample_file', 'database.views.sample_file', name='sample_file'),
    url(r'^shared_file', 'database.views.shared_file', name='shared_file'),
    url(r'^taxonomy_file', 'database.views.taxonomy_file', name='taxonomy_file'),
)


