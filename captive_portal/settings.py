import os

import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV = environ.Env()
ENV.read_env(os.path.join(BASE_DIR, '.env'))

RUNTIME_DIR = ENV.str('RUNTIME_DIR', os.path.join(BASE_DIR, 'runtime'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV.str('SECRET_KEY', 'I am insecure.')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV.bool('DEBUG', default=True)

ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS', default=['localhost'])

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if ENV.bool('FORCE_TLS', default=False):
	SESSION_COOKIE_SECURE = True
	CSRF_COOKIE_SECURE = True

SAML2_ENABLED = ENV.bool('SAML2_ENABLED', default=False)

ADMINS = (
	# ('Your Name', 'your_email@example.com'),
	(ENV.str('WEBMASTER_NAME', 'Webmaster'), ENV.str('WEBMASTER_EMAIL', 'root@localhost')),
)

MANAGERS = ADMINS

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'crispy_forms',
	'sass_processor',
	'captive_portal',
]

if SAML2_ENABLED:
	INSTALLED_APPS.append('django_saml2_auth')

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'formatters': {
		'console': {
			'format': '%(asctime)s %(name)s [%(levelname)s] %(message)s'
		}
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		},
		'console': {
			'level': 'DEBUG' if DEBUG else 'INFO',
			'formatter': 'console',
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'django': {
			'level': 'INFO',
			'handlers': ['console'],
		},
		'captive_portal': {
			'level': 'DEBUG',
			'handlers': ['console'],
		},
	}
}

MIDDLEWARE = (
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'xff.middleware.XForwardedForMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'captive_portal.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'site_tmpl')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'captive_portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
	'default': ENV.db(default="sqlite:///" + os.path.join(RUNTIME_DIR, 'db.sqlite3'))
}

# X-Forwarded-For

XFF_TRUSTED_PROXY_DEPTH = 1
XFF_STRICT = True
XFF_HEADER_REQUIRED = not DEBUG

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [] if DEBUG else [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

SAML2_AUTH = {
	'METADATA_AUTO_CONF_URL': ENV.str('SAML2_IDP_METADATA_URL', 'https://samltest.id/saml/idp'),
	'DEFAULT_NEXT_URL': '/',
	'CREATE_USER': True,
	'NEW_USER_PROFILE': {
		'USER_GROUPS': [],
		'ACTIVE_STATUS': True,
		'STAFF_STATUS': False,
		'SUPERUSER_STATUS': False,
	},
	'ATTRIBUTES_MAP': {
		'email': 'Email',
		'username': 'UserName',
		'first_name': 'FirstName',
		'last_name': 'LastName',
	},
	'ENTITY_ID': f'https://{ALLOWED_HOSTS[0]}/saml2_auth/acs/',
	'NAME_ID_FORMAT': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
	'USE_JWT': False,
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# For django-phonenumber-field
PHONENUMBER_DEFAULT_REGION = 'US'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ENV.str("STATIC_ROOT", os.path.join(RUNTIME_DIR, 'static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

STATICFILES_FINDERS = [
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'sass_processor.finders.CssFinder',
]

STATICFILES_DIRS = [
	# Additional static files directories
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
]

SASS_PROCESSOR_ROOT = os.path.join(STATIC_ROOT, 'css')

SASS_PROCESSOR_INCLUDE_DIRS = [
	os.path.join(BASE_DIR, 'node_modules'),
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Information for connecting to the UDM-Pro API
UNIFI_URL = ENV.str('UNIFI_URL', None)
UNIFI_SITE_ID = ENV.str('UNIFI_SITE_ID', None)
UNIFI_USERNAME = ENV.str('UNIFI_USERNAME', None)
UNIFI_PASSWORD = ENV.str('UNIFI_PASSWORD', None)

# How many minutes a successfully authorized device can use the Wi-Fi before it is sent to the captive portal again
AUTHENTICATED_USERS_AUTHORIZATION_MINUTES = ENV.int('AUTHENTICATED_USERS_AUTHORIZATION_MINUTES', 262800)
GUESTS_AUTHORIZATION_MINUTES = ENV.int('GUESTS_AUTHORIZATION_MINUTES', 1440)

# After authentication or in the event that a user visits the captive portal directly, the browser is redirected to
# this URL to (re-)trigger the UniFi controller to redirect the browser to the captive portal with the needed query
# parameters. This URL should be http, not https.
PORTAL_TRIGGER_REDIRECT = ENV.str('PORTAL_TRIGGER_REDIRECT', 'http://example.com/')

# An authenticated (non-guest) user is redirected to this URL after successfully gaining access to the Wi-Fi.
AUTHENTICATED_USERS_SUCCESS_REDIRECT = ENV.str('AUTHENTICATED_USERS_SUCCESS_REDIRECT', 'https://google.com/')

# A user that used the guest password is redirected to this URL after successfully gaining access to the Wi-Fi
GUESTS_SUCCESS_REDIRECT = ENV.str('GUESTS_SUCCESS_REDIRECT', 'https://google.com/')

# Requests from this source IP address are assumed NOT to be a device trying to connect to the Wi-Fi, and are not
# redirected to the PORTAL_TRIGGER_REDIRECT. They are instead redirected to this captive portal's user interface where
# they can perform other tasks.
REVERSE_PROXY_IP = ENV.str('REVERSE_PROXY_IP', '127.0.0.1')
