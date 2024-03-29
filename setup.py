#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages

with io.open('./src/attendancenudger/__init__.py', encoding='utf8') as version_file:
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
        where="src"
    ),
    # packages=['attendancenudger', 'lib', 'config'],
    package_dir={"": "src"},
    package_data={'':['*.txt', '_templates/*.html', '*.yml', '*.json']},
    exclude_package_data={'':['token.json']},
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    install_requires=[
        'arrow==0.14.5',
        'binaryornot==0.4.4',
        'biplist==1.0.3',
        'boto3==1.9.213',
        'botocore==1.12.213',
        'briefcase==0.2.9',
        'cachetools==5.0.0',
        'certifi==2019.6.16',
        'chardet==3.0.4',
        'Click==7.0',
        'cookiecutter==1.6.0',
        'dmgbuild==1.3.2',
        'docutils==0.15.2',
        'ds-store==1.1.2',
        'future==0.17.1',
        'google-api-core==2.7.1',
        'google-api-python-client==2.41.0',
        'google-auth==2.6.2',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==0.5.1',
        'googleapis-common-protos==1.56.0',
        'httplib2==0.20.4',
        'idna==2.8',
        'Jinja2==2.11.3',
        'jinja2-time==0.2.0',
        'jmespath==0.9.4',
        'mac-alias==2.0.7',
        'MarkupSafe==1.1.1',
        'numpy==1.17.1',
        'oauthlib==3.2.0',
        'poyo==0.5.0',
        'protobuf==3.19.4',
        'pyasn1==0.4.8',
        'pyasn1-modules==0.2.8',
        'PyJWT==1.7.1',
        'pyparsing==3.0.7',
        'PySocks==1.7.0',
        'python-dateutil==2.8.0',
        'pytz==2019.2',
        'PyYAML==5.4',
        'requests==2.22.0',
        'requests-oauthlib==1.3.1',
        'rsa==4.8',
        'rubicon-objc==0.3.1',
        's3transfer==0.2.1',
        'six==1.12.0',
        'SQLAlchemy==1.3.6',
        'toga==0.3.0.dev13',
        'toga-cocoa==0.3.0.dev13',
        'toga-core==0.3.0.dev13',
        'travertino==0.1.2',
        'twilio==6.29.3',
        'uritemplate==4.1.1',
        'urllib3==1.23',
        'voc==0.1.6',
        'whichcraft==0.6.0'
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
