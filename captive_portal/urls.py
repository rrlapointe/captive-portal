from django.conf import settings
from django.contrib import admin
from django.urls import include, path
import django_saml2_auth.views

from . import views

app_name = 'captive_portal' # pylint: disable=invalid-name

urlpatterns = []

if settings.SAML2_ENABLED:
	urlpatterns += [
		path('saml2_auth/', include('django_saml2_auth.urls')),
		path('accounts/login/', django_saml2_auth.views.signin, name='login'),
	]

# pylint: disable=invalid-name
urlpatterns += [
	path('', views.landing, name='landing1'),
	path('admin/', admin.site.urls),
	path('accounts/', include('django.contrib.auth.urls')),
	path('accounts/profile/', views.account_profile, name='myaccount'),
	path('guest/s/default/', views.landing, name='landing2'),
	path('authorize_guest', views.authorize_guest, name='authorize_guest'),
	path('ui/', include(([
		path('', views.homepage, name='home'),
		path('guest-password', views.guest_password, name='guest_password'),
		path('log', views.authorizations_list, name='authorizations_list'),
		path('netreg', views.AuthorizationCreateView.as_view(), name='netreg'),
		path('my-devices', views.my_devices, name='my_devices'),
	], 'captive_portal'), namespace='ui'))
]
