import os
from setuptools import setup

# variables used in buildout
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'pytest-runner',
    'boto3',
    'Submit4DN',
    'dcicutils',
]

tests_require = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
]

setup(
    name='wrangling',
    version=open(
        "wrangling/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    description='Scripts for wrangling - things not ready for other packages',
    long_description=README,
    packages=['wrangling'],
    include_package_data=True,
    zip_safe=False,
    author='Andy Schroeder',
    author_email='andrew_schroeder@hms.harvard.edu',
    license='MIT',
    install_requires=requires,
    setup_requires=requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
)
