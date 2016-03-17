#!/usr/bin/env python

"""
hansel
------

Flexible parametric file paths to make queries, build folder trees and
smart folder structure access.
"""

from __future__ import print_function

import os.path as op
import io
import sys

from   setuptools              import setup, find_packages
from   setuptools.command.test import test as TestCommand


# long description
def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


# Get version without importing, which avoids dependency issues
MODULE_NAME = find_packages(exclude=['tests'])[0]
VERSION_PYFILE = op.join(MODULE_NAME, 'version.py')
# set __version__ variable
exec(compile(read(VERSION_PYFILE), VERSION_PYFILE, 'exec'))


setup_dict = dict(
    name=MODULE_NAME,
    version=__version__,
    description='from hansel import Crumb to find your file path.',

    url='https://pypi.python.org/pypi/hansel',
    license='Apache 2.0',
    author='alexsavio',
    author_email='alexsavio@gmail.com',
    maintainer='alexsavio',
    maintainer_email='alexsavio@gmail.com',

    packages=find_packages(),

    install_requires=['six'],

    scripts=[],

    long_description=read('README.rst', 'CHANGES.rst'),

    platforms='Linux/MacOSX',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
    ],

    extras_require={
        'testing': ['pytest', 'pytest-cov', 'pandas'],
    }
)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup_dict.update(dict(tests_require=['pytest'],
                       cmdclass={'test': PyTest}))


if __name__ == '__main__':
    setup(**setup_dict)
