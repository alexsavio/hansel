#!/usr/bin/env python

"""
hansel
------

Flexible parametric file paths to make queries, build folder trees and
smart folder structure access.
"""
import io

from setuptools import setup, find_packages


requirements = [
    'click>=6.7',
]


# long description
def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


setup_dict = dict(
    name='hansel',
    version='2.0.1',
    description='Easily traverse your structured folder tree.',
    url='https://pypi.python.org/pypi/hansel',
    license='Apache 2.0',
    author='alexsavio',
    author_email='alexsavio@gmail.com',
    maintainer='alexsavio',
    maintainer_email='alexsavio@gmail.com',
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,

    entry_points='''
      [console_scripts]
      crumb=hansel.cli:cli
      ''',

    long_description=read('README.rst', 'CHANGES.rst'),
    platforms='Linux/MacOSX',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.6',
    ],
)

if __name__ == '__main__':
    setup(**setup_dict)
