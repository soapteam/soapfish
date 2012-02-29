from setuptools import setup

setup(
    name='soapbox',
    version='0.2.0',
    author='Damian Powazka',
    author_email='dpowazka@gmail.com',
    url='http://code.google.com/p/soapbox/',
    description='Python Django-like SOAP library',
    download_url='',
    license='New BSD',
    install_requires=['argparse', 'jinja2', 'lxml'],
    packages=['soapbox'],
    entry_points={
        'console_scripts': [
            'py2wsdl=soapbox.py2wsdl:main',
            'py2xsd=soapbox.py2xsd:main',
            'wsdl2py=soapbox.wsdl2py:main',
            'xsd2py=soapbox.xsd2py:main',
        ],
    },
    platforms='Python 2.6 and later.',
    classifiers=[
        'Development Status :: 2 - Beta',
        'License :: OSI Approved :: New BSD',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Intended Audience :: Science/Research',
    ],
)
