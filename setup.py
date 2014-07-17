#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) Damian Powązka and Flight Data Services, Ltd.
# See the file "LICENSE" for the full license governing this code.

import soapbox as pkg
from setuptools import setup, find_packages
from requirements import RequirementsParser
requirements = RequirementsParser()

setup(
    name=pkg.__packagename__,
    version=pkg.__version__,
    author=pkg.__author__,
    author_email=pkg.__author_email__,
    maintainer=pkg.__maintainer__,
    maintainer_email=pkg.__maintainer_email__,
    url=pkg.__url__,
    description=pkg.__description__,
    long_description=open('README.rst').read() + open('CHANGES').read() +
    open('TODO').read() + open('AUTHORS').read(),
    download_url=pkg.__download_url__,
    classifiers=pkg.__classifiers__,
    platforms=pkg.__platforms__,
    license=pkg.__license__,
    keywords=pkg.__keywords__,
    packages=find_packages(exclude=('examples', 'tests',)),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements.install_requires,
    setup_requires=requirements.setup_requires,
    tests_require=requirements.tests_require,
    extras_require=requirements.extras_require,
    dependency_links=requirements.dependency_links,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'py2wsdl=soapbox.py2wsdl:main',
            'py2xsd=soapbox.py2xsd:main',
            'wsdl2py=soapbox.wsdl2py:main',
            'xsd2py=soapbox.xsd2py:main',
        ],
    },
    package_data={
        'soapbox.templates': ['wsdl', 'xsd'],
    },
)

################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
