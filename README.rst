hansel
======

Flexible parametric file paths to make queries, build folder trees and smart
folder structure access.

|Build Status| |Coverage Status|

Usage
=====

Quick Intro
-----------

Imagine this folder tree:

::

    data
    └── raw
        ├── 0040000
        │   └── session_1
        │       ├── anat_1
        │       └── rest_1
        ├── 0040001
        │   └── session_1
        │       ├── anat_1
        │       └── rest_1
        ├── 0040002
        │   └── session_1
        │       ├── anat_1
        │       └── rest_1
        ├── 0040003
        │   └── session_1
        │       ├── anat_1
        │       └── rest_1
        ├── 0040004
        │   └── session_1
        │       ├── anat_1
        │       └── rest_1


.. code:: python

    from hansel import Crumb

    # create the crumb
    crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}/{image}")

    # set the base_dir path
    crumb = crumb.replace('base_dir', '/home/hansel')

    assert str(crumb) == "/home/hansel/data/raw/{subject_id}/{session_id}/{image_type}"

    # get the ids of the subjects
    subj_ids = crumb['subject_id']

    assert subj_ids == ['0040000', '0040001', '0040002', '0040003', '0040004', ....]

    # get the paths to the subject folders, the output can be strings or crumbs, you choose with the make_crumbs boolean argument
    subj_paths = crumb.ls('subject_id', make_crumbs=True)

    # set the image_type
    anat_crumb = crumb.replace(image_type='anat_1')

    # get the paths to the anat_1 folders
    anat_paths = anat_crumb.ls('image')


Long Intro
----------

I often find myself in a work related with structured folder paths, such as the
one shown above.

I have tried many ways of solving these situations: loops, dictionaries,
configuration files, etc. I always end up doing a different thing for the same
problem over and over again.

This week I grew tired of it and decided to make a representation of a
structured folder tree in a string and access it the most easy way.

If you look at the folder structure above I have:

-  the root directory from where it is hanging: ``...data/raw``,
-  many identifiers (in this case a subject identification), e.g.,
   ``0040000``,
-  session identification, ``session_1`` and
-  a data type (in this case an image type), ``anat_1`` and ``rest_1``.

With ``hansel`` I can represent this folder structure like this:

.. code:: python

    from hansel import Crumb

    crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}")


Let's say we have the structure above hanging from a base directory like ``/home/hansel/``.

I can use the ``replace`` function to make set the ``base_dir``
parameter:

.. code:: python

    crumb = crumb.replace('base_dir', '/home/hansel')

    assert str(crumb) == "/home/hansel/data/raw/{subject_id}/{session_id}/{image_type}"

if you don't need a copy of ``crumb``, you can use the ``[]`` operator:

.. code:: python

    crumb['base_dir'] = '/home/hansel'


Now that the root path of my dataset is set, I can start querying my
crumb path.

If I want to know the path to the existing ``subject_ids`` folders:

.. code:: python

    subject_paths = anat_crumb.ls('subject_id')

The output of ``ls`` can be ``str`` or ``Crumb`` or ``pathlib.Path``.
They will be ``Path`` if there are no crumb arguments left in the crumb path.
You can choose this using the ``make_crumbs`` argument:

.. code:: python

    subject_paths = anat_crumb.ls('subject_id', make_crumbs=True)

If I want to know what are the existing ``subject_ids``:

.. code:: python

    subject_ids = crumb.ls('subject_id', fullpath=False)

or

.. code:: python

    subject_ids = crumb['subject_id']

Now, if I wanted to get the path to all the ``anat_1`` images, I could
do this:

.. code:: python

    anat_crumb = crumb.replace(image_type='anat_1')

    anat_paths = anat_crumb.ls('image')

or

.. code:: python

    crumb['image_type'] = 'anat_1'

    anat_paths = crumb.ls('image')


There are more features such as creating folder trees with a value of maps for the crumbs and also
check the feasibility of a crumb path.

More functionalities, ideas and comments are welcome.


Dependencies
============

Please see the requirements.txt file. Before installing this package,
install its dependencies with:

    pip install -r requirements.txt


Install
=======

I am only testing this tool on Python 3.4 and 3.5. Maybe it works on Python 2.7 as well as for the parts related with
strings (very few) I am using `six`.

This package uses setuptools. You can install it running:

    python setup.py install

If you already have the dependencies listed in requirements.txt
installed, to install in your home directory, use:

    python setup.py install --user

To install for all users on Unix/Linux:

    | python setup.py build
    | sudo python setup.py install

You can also install it in development mode with:

    python setup.py develop


Development
===========

Code
----

Github
~~~~~~

You can check the latest sources with the command:

    git clone https://www.github.com/alexsavio/hansel.git

or if you have write privileges:

    git clone git@github.com:alexsavio/hansel.git

If you are going to create patches for this project, create a branch
for it from the master branch.

We tag stable releases in the repository with the version number.

Testing
-------

We are using `py.test <http://pytest.org/>`__ to help us with the testing.

Otherwise you can run the tests executing:

    python setup.py test

or

    py.test

.. |Build Status| image:: https://travis-ci.org/alexsavio/hansel.svg?branch=master
   :target: https://travis-ci.org/alexsavio/hansel
.. |Coverage Status| image:: https://coveralls.io/repos/alexsavio/hansel/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/alexsavio/hansel?branch=master
