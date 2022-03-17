#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

with io.open('./attendancenudger/__init__.py', encoding='utf8') as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open('README.md', encoding='utf8') as readme:
    long_description = readme.read()


setup(
    name='attendancenudger',
    version=version,
    description='An app that does lots of stuff',
    long_description=long_description,
    author='James Vorderbruggen',
    author_email='jamesvorder@riseup.net',
    license='GNU General Public License v3 (GPLv3)',
    packages=find_packages(
        exclude=[
            'docs', 'tests',
            'windows', 'macOS', 'linux',
            'iOS', 'android',
            'django'
        ]
    ), 
    package_data={'':['*.txt', '_templates/*.html', '*.yml']},
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    install_requires=[
        'certifi==2019.6.16',
        'chardet==3.0.4',
        'idna==2.8',
        'Jinja2==2.11.3',
        'MarkupSafe==1.1.1',
        'PyJWT==1.7.1',
        'PySocks==1.7.0',
        'pytz==2019.2',
        'PyYAML==5.1.2',
        'requests==2.22.0',
        'six==1.12.0',
        'SQLAlchemy==1.3.6',
        'twilio==6.29.3',
        'urllib3==1.24.3',
	'numpy==1.17.1',
	'setuptools==41.2.0',
        ], 
    #options={
    #    'app': {
    #        'formal_name': 'Attendance Nudger',
    #        'bundle': 'com.mindthegap'
    #    },

    #    # Desktop/laptop deployments
    #    'macos': {
    #        'app_requires': [
    #        ]
    #    },
    #    'linux': {
    #        'app_requires': [ 
    #            ]
    #    },
    #    'windows': {
    #        'app_requires': [
    #        ]
    #    },

    #    # Mobile deployments
    #    'ios': {
    #        'app_requires': [
    #        ]
    #    },
    #    'android': {
    #        'app_requires': [
    #        ]
    #    },

    #    # Web deployments
    #    'django': {
    #        'app_requires': [
    #        ]
    #    },
    #}
)
