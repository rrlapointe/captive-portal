#!/usr/bin/env python

import os
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
	README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='captive-portal',
	version='1.0.0',
	packages=find_packages(),
	include_package_data=True,
	scripts=['manage.py'],
	license='MIT',
	description='Captive portal with SAML2 SSO for networks that use Ubiquiti UDM-Pro',
	long_description=README,
	author='Ryan LaPointe',
	author_email='ryan@ryanlapointe.org',
	python_requires='>=3.7.3',
	install_requires=[
		'Django<4.0',
		'django-environ',
		'django-crispy-forms',
		'crispy-bootstrap4',
		'django-sass-processor',
		'django-macaddress',
		'timeago',
		'django-xff',
		'django-saml2-auth',
	],
	extras_require={
		'dev': [
			'libsass',
			'django-compressor',
			'bpython',
		],
		'nginx': [
			'gunicorn',
		]
	}
)
