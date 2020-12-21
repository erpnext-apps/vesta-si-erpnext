# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in vesta_si_erpnext/__init__.py
from vesta_si_erpnext import __version__ as version

setup(
	name='vesta_si_erpnext',
	version=version,
	description='A custom Frappe App for Vesta Si Sweden AB',
	author='Frappe Technologies Pvt. Ltd.',
	author_email='developers@frappe.io',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
