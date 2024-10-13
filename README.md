# Captive portal

![lint](https://github.com/rrlapointe/captive-portal/workflows/lint/badge.svg)

This is a captive portal that interfaces with the Ubiquiti UniFi Dream Machine Pro to authorize clients on the Wi-Fi. Users sign in via SAML2 SSO and guests enter a password. The guest password rotates daily and can be retrieved by authenticated users for giving to a guest. The site provides a form for authenticated users to authorize devices that are incompatible with captive portals by entering the devices' MAC addresses. The site keeps a log of successful authorizations.

The app is written in Python 3 and uses the Django framework.

## Production Deployment

Here are some Django documentation pages that describe ways to set up for production.
- [Setting up Apache with mod_wsgi](https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/modwsgi/)
- [Setting up uWSGI, which can be used with nginx, Apache, or other web server](https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/uwsgi/)
- [Setting up Gunicorn, which can be used with nginx, Apache, or other web server](https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/gunicorn/)

The general process of setting up a Django web app for production is outside the scope of this document. This section covers configuration steps that are specific to this app.

You probably want to personalize the captive portal landing page by editing [site_tmpl/landing.html](./site_tmpl/landing.html).

### Environment variables

The app can be configured through environment variables or through a `.env` file. Below is an example `.env` file. You should create a `.env` file similar to the example or set all of the environment variables shown in the example. If you use a `.env` file, you should set the file permissions such that it can be read only by the user that runs the app.

```
DEBUG=false
STATIC_ROOT=/var/www/captive-portal-static/static
MEDIA_ROOT=/var/www/captive-portal-static/media
RUNTIME_DIR=/srv/captive-portal/runtime
ALLOWED_HOSTS=captive-portal.example.org,192.168.0.2
SECRET_KEY=example
WEBMASTER_EMAIL=webmaster@example.org
SAML2_ENABLED=true
SAML2_IDP_METADATA_URL=https://portal.sso.us-east-1.amazonaws.com/saml/metadata/example
UNIFI_URL=https://192.168.0.1/
UNIFI_SITE_ID=default
UNIFI_USERNAME=example
UNIFI_PASSWORD=example
PORTAL_TRIGGER_REDIRECT=http://example.org/
AUTHENTICATED_USERS_SUCCESS_REDIRECT=https://example.org/
GUESTS_SUCCESS_REDIRECT=https://example.org/guest/
REVERSE_PROXY_IP=192.168.0.3
```

#### UNIFI_URL

The URL of the UDM Pro.

#### UNIFI_SITE_ID

Set to `default`.

#### UNIFI_USERNAME

The username of the local user that you created on the UDM Pro for the captive portal.

#### UNIFI_PASSWORD

The password of the local user that you created on the UDM Pro for the captive portal.

#### PORTAL_TRIGGER_REDIRECT

When an unauthorized device on the WiFi attempts to access a website, the UniFi network will redirect it to the captive portal with a query parameter in the URL that tells the captive portal the MAC address of the device. When a user navigates directly to the captive portal without being redirected by the UniFi network, that query paramter is missing.

When that query parameter is missing, the captive portal will redirect to the URL specified by the PORTAL_TRIGGER_REDIRECT environment variable in an attempt to trigger the captive portal function of the UniFi network, which will redirect back to the captive portal with the required query parameter.

#### AUTHENTICATED_USERS_SUCCESS_REDIRECT

The captive portal will redirect to this URL after successfully authorizing a user with SAML.

#### GUESTS_SUCCESS_REDIRECT

The captive portal will redirect to this URL after successfully authorizing a guest with the guest password.

#### REVERSE_PROXY_IP

This is the IP address of the reverse proxy that allows the captive portal to be accessed from outside the LAN. When a request comes from this IP address, the captive portal will not redirect to the PORTAL_TRIGGER_REDIRECT URL.

### Installing dependencies

[requirements.txt](./requirements.txt) contains a list of pinned dependencies that have been tested together and confirmed to work. [setup.py](./setup.py) does not pin dependencies. Installing with `setup.py` (e.g. `pip install .`) is more likely to result in a broken installation than installing with `requirements.txt` (e.g. `pip install -r requirements.txt`), but it is also less likely to install versions with known security vulnerabilities.

## Development

To run the app on your local development machine for the first time, run the following commands in the project root directory.

```sh
foo@bar:~/somewhere/captive-portal$ npm install
foo@bar:~/somewhere/captive-portal$ python3 -m venv venv
foo@bar:~/somewhere/captive-portal$ . venv/bin/activate
(venv) foo@bar:~/somewhere/captive-portal$ pip install --upgrade pip
(venv) foo@bar:~/somewhere/captive-portal$ pip install -e .[dev]
(venv) foo@bar:~/somewhere/captive-portal$ mkdir runtime
(venv) foo@bar:~/somewhere/captive-portal$ python manage.py migrate
(venv) foo@bar:~/somewhere/captive-portal$ python manage.py createsuperuser
(venv) foo@bar:~/somewhere/captive-portal$ python manage.py runserver
```

To run the app again, run the following commands in the project root directory.

```sh
foo@bar:~/somewhere/captive-portal$ . venv/bin/activate
(venv) foo@bar:~/somewhere/captive-portal$ python manage.py runserver
```
