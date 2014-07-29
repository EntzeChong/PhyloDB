from django.conf.urls import patterns, include, url
from django.contrib import admin

#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'phyloDB.views.home', name='home'),


    url(r'^admin/', include(admin.site.urls)),
    (r'^home/$', 'database.views.home'),
)
