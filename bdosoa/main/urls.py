from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'bdosoa.main.views.index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^API/$', 'bdosoa.main.views.api'),
    url(r'^SOAP/$', 'bdosoa.main.views.soap'),
    url(r'^SOAP/(?P<token>\w+)/$', 'bdosoa.main.views.soap'),
)
