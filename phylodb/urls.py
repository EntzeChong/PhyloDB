from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^home/$', 'database.views.home'),
    url(r'^upload/$', 'database.views.upload', name='upload'),
    url(r'^select/$', 'database.views.select'),
    url(r'^norm/$', 'database.views.norm'),
    url(r'^graph/$', 'database.views.graph'),
    url(r'^treeProject', 'treeProject.views.treeProject', name='treeProject'),
    url(r'^treeMeta', 'treeMeta.views.treeMeta', name='treeMeta'),
    url(r'^treeTaxonomy', 'treeTaxonomy.views.treeTaxonomy', name='treeTaxonomy'),
  #  url(r'^getGraphData', 'treeTaxonomy.views.getGraphData', name='getGraphData'),
  #  url(r'^getTableData', 'treeTaxonomy.views.getTableData', name='getTableData'),
)

