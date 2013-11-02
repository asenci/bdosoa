from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'bdo.main.views.index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^SOAP/', 'bdo.main.views.soap_app')
)
