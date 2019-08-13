#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

#with io.open('./{{ cookiecutter.app_name }}/__init__.py', encoding='utf8') as version_file:
#    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
#    if version_match:
#        version = version_match.group(1)
#    else:
#        raise RuntimeError("Unable to find version string.")


#with io.open('README.rst', encoding='utf8') as readme:
#    long_description = readme.read()


setup(
    name='Attendance Nudger',
    #version=version,
    description='An app.',
    #long_description="",
    #author='{{ cookiecutter.author }}',
    #author_email='{{ cookiecutter.author_email }}',
    #license='{{ cookiecutter.license }}',
    #packages=find_packages(
    #    exclude=[
    #        'docs', 'tests',
    #        'windows', 'macOS', 'linux',
    #        'iOS', 'android',
    #        'django'
    #    ]
    #),
    #classifiers=[
    #    'Development Status :: 1 - Planning',
    #    'License :: OSI Approved :: {{ cookiecutter.license }}',
    #],
    #install_requires=[{% if cookiecutter.gui_framework == 'PySide2' %}
    #    'pyside2==5.13.0',{% endif %}
    #],
    options={
        'app': {
            'formal_name': 'Attendace Nudger',
            'bundle': 'com.attendancenudger'
        },

        # Desktop/laptop deployments
        'macos': {
            'app_requires': [
                'certifi==2019.6.16',
                'chardet==3.0.4',
                'idna==2.8',
                'Jinja2==2.10.1',
                'MarkupSafe==1.1.1',
                'PyJWT==1.7.1',
                'PySocks==1.7.0',
                'pytz==2019.2',
                'PyYAML==5.1.2',
                'requests==2.22.0',
                'six==1.12.0',
                'SQLAlchemy==1.3.6',
                'twilio==6.29.3',
                'urllib3==1.25.3',
            ]
        }
    }
)
