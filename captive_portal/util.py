from datetime import date
import json
from random import Random
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def calculate_guest_password():
	with open('wordlist.txt', 'r', encoding='ascii') as wordlist_file:
		wordlist = wordlist_file.read().splitlines()
	random = Random(settings.SECRET_KEY + 'guest_password' + str(date.today()))
	return ' '.join(random.choices(wordlist, k=3))

def authorize(mac, minutes):
	if None in (settings.UNIFI_URL, settings.UNIFI_SITE_ID, settings.UNIFI_USERNAME, settings.UNIFI_PASSWORD):
		print('UniFi API has not been configured, so skipping the API calls.')
		return

	login_url = f'{settings.UNIFI_URL}api/auth/login'
	logout_url = f'{settings.UNIFI_URL}api/auth/logout'
	api_url = f'{settings.UNIFI_URL}proxy/network/api/s/{settings.UNIFI_SITE_ID}/cmd/stamgr'

	auth = {
		'cmd': 'authorize-guest',
		'mac': mac,
		'minutes': minutes,
	}

	auth_params = {
		'json': json.dumps(auth)
	}

	# Use a Session object to handle cookies.
	with requests.Session() as session:
		session.verify = False
		# Log in to the API
		response = session.post(login_url, data={
			'username': settings.UNIFI_USERNAME,
			'password': settings.UNIFI_PASSWORD
		}, timeout=5)
		if response.status_code != 200:
			raise ImproperlyConfigured(f'Response from UniFi: {response.status_code} {response.content}')
		session.headers['x-csrf-token'] = response.headers.get('x-csrf-token')

		# Authorize the client
		response = session.post(api_url, data=auth_params, timeout=5)
		if response.status_code != 200:
			session.post(logout_url, timeout=5)
			raise ImproperlyConfigured(f'Response from UniFi: {response.status_code} {response.content}')

		# Log out from the API
		session.post(logout_url, timeout=5)
