from setuptools import setup

setup(name='mor-api-services', 
    version='0.0.1',
    description='Melding Openbare Ruimte API Services for django app', 
    url='https://github.com/forza-mor-rotterdam/mor-api-services', 
    author='mguikema', 
    author_email='', 
    license='EUPL', 
    packages=['mor_api_services'],
    install_requires=
    [
        'Django>=4.2.15',
        'requests>=2.29.0',
    ],      
    zip_safe=False)