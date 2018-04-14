from setuptools import setup, find_packages

""" initial one, needs tidying up"""
setup(name='makers',
    version='0.0.1',
    description='makers',
    author='',
    author_email='',
    license='',
    install_requires = [
        'pymongo',
        'yaml'
    ],
    packages=find_packages())
