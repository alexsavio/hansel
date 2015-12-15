.. -*- mode: rst -*-

hansel
======

Flexible parametric file paths to make queries, build folder trees and
smart folder structure access.

.. image:: https://secure.travis-ci.org/alexsavio/hansel.png?branch=master
    :target: https://travis-ci.org/alexsavio/hansel

.. image:: https://coveralls.io/repos/alexsavio/hansel/badge.png
    :target: https://coveralls.io/r/alexsavio/hansel


Dependencies
============

Please see the requirements.txt file. Before installing this package, install its dependencies with:

    pip install -r requirements.txt


Install
=======

This package uses setuptools. You can install it running:

    python setup.py install

If you already have the dependencies listed in requirements.txt installed,
to install in your home directory, use::

    python setup.py install --user

To install for all users on Unix/Linux::

    python setup.py build
    sudo python setup.py install

You can also install it in development mode with::

    python setup.py develop


Development
===========

Code
----

Github
~~~~~~

You can check the latest sources with the command::

    git clone https://www.github.com/alexsavio/hansel.git

or if you have write privileges::

    git clone git@github.com:alexsavio/hansel.git

If you are going to create patches for this project, create a branch for it
from the master branch.

We tag stable releases in the repository with the version number.


Testing
-------

We are using [pytest](http://pytest.org) to help us with the testing.
If you don't have pytest installed you can run the tests using:

    ./runtests.py

Otherwise you can run the tests executing:

    python setup.py test

or

    pytest
