from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in meeting_management/__init__.py
from meeting_management import __version__ as version

setup(
	name="meeting_management",
	version=version,
	description="meeting",
	author="Finbyz Tech PVT LTD",
	author_email="info@finbyz.tech",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
