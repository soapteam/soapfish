#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Soapbox is a SOAP library for Python capable of generating Python modules from
WSDL documents and providing a dispatcher for the Django framework.
'''

import re

from setuptools import setup, find_packages

import soapbox


def requires_from_file(filename):
    requirements = []
    with open(filename, 'r') as requirements_fp:
        for line in requirements_fp.readlines():
            match = re.search('^\s*([a-zA-Z][^#]+?)(\s*#.+)?\n$', line)
            if match:
                requirements.append(match.group(1))
    return requirements

setup(
    name='soapbox-bsd',
    version=soapbox.__version__,
    author=soapbox.__author__,
    author_email=soapbox.__email__,
    url='https://github.com/FelixSchwarz/soapbox-bsd',
    description='A SOAP library for Python',
    long_description=open('README.md').read() + open('CHANGES').read() + open('TODO').read(),
    download_url='',
    license='New BSD License',
    packages=find_packages(exclude=("examples", "tests",)),
    include_package_data=True,
    install_requires=requires_from_file('requirements.txt'),
    tests_require=requires_from_file('dev_requirements.txt'),
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'py2wsdl=soapbox.py2wsdl:main',
            'py2xsd=soapbox.py2xsd:main',
            'wsdl2py=soapbox.wsdl2py:main',
            'xsd2py=soapbox.xsd2py:main',
        ],
    },
    platforms=['OS Independent'],
    keywords=['SOAP', 'WSDL', 'web service'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
