#!/usr/bin/env python

from distutils.core import setup

setup(
	name='codebase-api-client',
	version='1.1',
	description='A Python client for the Codebase API',
	author='Phil Tysoe',
	author_email='philtysoe@gmail.com',
	url='https://github.com/igniteflow/codebase-python-api-client',
	packages=['codebase'],
	install_requires=[
		'requests>=2.0.1',
	],
	license='MIT',
)