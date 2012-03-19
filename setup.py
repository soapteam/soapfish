#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################

'''
Soapbox is a SOAP library for Python capable of generating Python modules from
WSDL documents and providing a dispatcher for the Django framework.
'''


try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


import soapbox
from requirements import RequirementsParser


requirements = RequirementsParser()


setup(
    name='soapbox',
    version=soapbox.__version__,
    author=soapbox.__author__,
    author_email=soapbox.__email__,
    url='http://code.google.com/p/soapbox/',
    description='A SOAP library for Python',
    long_description=open('README').read() + open('CHANGES').read() + open('TODO').read(),
    download_url='',
    license='New BSD License',
    packages=find_packages(exclude=("examples", "tests",)),
    include_package_data=True,
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


################################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
