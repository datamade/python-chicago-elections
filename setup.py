#!/usr/bin/env python

from setuptools import setup, find_packages

# PyPI only supports nicely-formatted README files in reStructuredText.
# Use a version of the pattern from
# https://coderwall.com/p/qawuyq/use-markdown-readme-s-in-python-modules
# to convert the Markdown README to rst if the pypandoc package is
# present.
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError):
    long_description = open('README.md').read()

# Load the version from the clarify.version module
exec(open('chi_elections/version.py').read())

setup(
    name='chi-elections',
    version=__version__,
    author='Chicago Tribune News Applications',
    author_email='newsapps@tribune.com',
    url='https://github.com/newsapps/',
    description=('A library for scraping and parsing election results from '
                 'the Chicago Board of Elections'),
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'lxml',
        'six',
        'Click',
        'backports.csv'
    ],
    entry_points={
        'console_scripts': (
            'chi_elections = chi_elections.cli:main'
        ),
    },
    keywords=['elections', 'Chicago', 'results', 'parser', 'scraper'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing',
    ],
)
