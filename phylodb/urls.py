from django.conf.urls import patterns, include, url
import treePlotter

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/$', 'database.views.home'),
    url(r'^upload/$', 'database.views.upload'),
    url(r'^select/$', 'database.views.select'),
    url(r'^norm/$', 'database.views.norm'),
    #url(r'^getTree', treePlotter.views.getTree, name='getTree')
)

