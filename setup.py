from distutils.core import setup
from setuptools import find_packages


setup(
    name='cartridge-stripe',
    version='0.1.3',
    author='Timothy Watts (readevalprint)',
    author_email='tim@readevalprint.com',
    packages=find_packages(),
    url='https://github.com/readevalprint/cartridge-stripe/',
    license='LICENSE.txt',
    include_package_data=True,
    description='Stripe credit card processing integration with Cartridge',
    long_description=open('README.rst').read(),
)
