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
    url(r'^request/restore/password/$', RequestRestorePassword.as_view(), name='request_restore_password'),
    url(r'^password/restore/(?P<code>[a-zA-Z0-9]*)/$', PasswordRestoreView.as_view(), name='restore_pass'),
    url(r'^$', RegisterView.as_view(), name='registration'),
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^cabinet/', CabinetView.as_view(), name='cabinet'),

)
