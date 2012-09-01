from distutils.core import setup

setup(
    name='cartridge-stripe',
    version='0.1.0',
    author='Timothy Watts (readevalprint)',
    author_email='tim@readevalprint.com',
    packages=['cartridge_stripe'],
    url='https://github.com/readevalprint/cartridge-stripe/',
    license='LICENSE.txt',
    description='Stripe credit card processing integration with Cartridge',
    long_description=open('README.md').read(),
)
