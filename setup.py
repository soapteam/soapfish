#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import sys

from setuptools import find_packages, setup

import soapfish

if sys.version_info < (2, 6) or (3, 0) <= sys.version_info < (3, 3):
    sys.stderr.write('Soapfish requires Python 2.6, 2.7 or 3.3+')
    sys.exit(1)


def description(*filenames):
    items = []
    for filename in filenames:
        with open(filename, 'r') as f:
            items.append(f.read().strip())
    return '\n\n'.join(items)


def requirements(*filenames):
    items = []
    for filename in filenames:
        with open(filename, 'r') as f:
            for line in f.readlines():
                match = re.search('^([a-zA-Z][^#]+?)(\s*#.+)?$', line.strip())
                if match:
                    items.append(match.group(1))
    return items


setup(
    name='soapfish',
    version=soapfish.__version__,
    author=soapfish.__author__,
    author_email=soapfish.__email__,
    maintainer='Felix Schwarz',
    maintainer_email='felix.schwarz@oss.schwarz.eu',
    url='http://soapfish.org/',
    download_url='http://soapfish.org/releases/',
    description='A SOAP library for Python',
    long_description=description('README.md', 'AUTHORS.md', 'CHANGES.md', 'TODO.md'),
    license='BSD',
    packages=find_packages(exclude=['examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements('requirements.txt'),
    tests_require=requirements('dev_requirements.txt'),
    test_suite='nose.collector',
    obsoletes=['soapbox'],
    entry_points={
        'console_scripts': [
            'py2wsdl=soapfish.py2wsdl:main',
            'py2xsd=soapfish.py2xsd:main',
            'wsdl2py=soapfish.wsdl2py:main',
            'xsd2py=soapfish.xsd2py:main',
        ],
    },
    platforms=['OS Independent'],
    keywords=['soap', 'wsdl', 'xsd', 'xml', 'schema', 'web service'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Flask',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
