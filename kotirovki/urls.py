from django.conf.urls import patterns, include, url
from .views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('kotirovki.views',
    # Examples:
    # url(r'^$', 'kotirovki.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^email/activate/(?P<code>[a-zA-Z0-9]*)/$', 'activate_account', name='activate'),
    url(r'^registration/', RegisterView.as_view(), name='registration'),
    url(r'^login/', LoginView.as_view(), name='login'),
)
