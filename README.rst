hansel
======

Parametric file paths to access and build structured folder trees.

|PyPI| |Build Status| |Coverage Status| |PyPI Downloads| |Code Health| |Scrutinizer|

It almost doesn't have `Dependencies`_, check how to `Install`_ it.

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

    >>> from hansel import Crumb

    # create the crumb
    >>> crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}/{image}")

    # set the base_dir path
    >>> crumb = crumb.replace(base_dir='/home/hansel')
    >>> print(str(crumb))
    /home/hansel/data/raw/{subject_id}/{session_id}/{image_type}

    # get the ids of the subjects
    >>> subj_ids = crumb['subject_id']
    >>> print(subj_ids)
    ['0040000', '0040001', '0040002', '0040003', '0040004', '0040005', ...

    # get the paths to the subject folders, the output can be strings or crumbs,
    # you choose with the ``make_crumbs`` boolean argument. Default: True.
    >>> subj_paths = crumb.ls('subject_id', make_crumbs=True)
    >>> print(subj_paths)
    [Crumb("/home/hansel/data/raw/0040000/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040001/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040002/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040003/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040004/{session_id}/{image_type}/{image}"),
     ...

    # set the image_type
    >>> anat_crumb = crumb.replace(image_type='anat_1')
    >>> print(anat_crumb)
    /home/hansel/data/raw/{subject_id}/{session_id}/anat_1/{image}

    # get the paths to the images inside the anat_1 folders
    >>> anat_paths = anat_crumb.ls('image')
    >>> print(anat_paths)
    [Crumb("/home/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040004/session_1/anat_1/mprage.nii.gz"),
     ...

    # get the ``session_id`` of each of these ``anat_paths``
    >>> sessions = [cr['session_id'] for cr in anat_paths]
    >>> print(sessions)
    ['session_1', 'session_1', 'session_1', 'session_1', 'session_1', ...

    # if you don't want the the output to be ``Crumbs`` but string paths:
    >>> anat_paths = anat_crumb.ls('image', make_crumbs=False)
    >>> print(anat_paths)
    ["/home/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz",
     "/home/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz",
     "/home/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz",
     "/home/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz",
     "/home/hansel/data/raw/0040004/session_1/anat_1/mprage.nii.gz",
     ...

    # you can also use a list of ``fnmatch`` expressions to ignore certain files patterns
    # using the ``ignore_list`` argument in the constructor.
    # For example, the files that start with '.'.
    >>> crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}/{image}",
    >>>               ignore_list=['.*'])

See more quick examples after the `Long Intro`_ check `More features and tricks`_.

---------------------

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

    >>> from hansel import Crumb
    >>> crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}/{image}")

Let's say we have the structure above hanging from a base directory like ``/home/hansel/``.

I can use the ``replace`` function to make set the ``base_dir`` parameter:

.. code:: python

    >>> crumb = crumb.replace(base_dir='/home/hansel')
    >>> print(str(crumb))
    /home/hansel/data/raw/{subject_id}/{session_id}/{image_type}

if I don't need a copy of ``crumb``, I can use the ``[]`` operator:

.. code:: python

    >>> crumb['base_dir'] = '/home/hansel'
    >>> print(str(crumb))
    /home/hansel/data/raw/{subject_id}/{session_id}/{image_type}

Now that the root path of my dataset is set, I can start querying my
crumb path.

If I want to know the path to the existing ``subject_id`` folders:

We can use the ``ls`` function. Its output can be ``str`` or ``Crumb``.
I can choose this using the ``make_crumbs`` argument (default: True):

.. code:: python

    >>> subj_crumbs = crumb.ls('subject_id')
    >>> print(subj_crumbs)
    [Crumb("/home/hansel/data/raw/0040000/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040001/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040002/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040003/{session_id}/{image_type}/{image}"),
     Crumb("/home/hansel/data/raw/0040004/{session_id}/{image_type}/{image}"),
     ...

    >>> subj_paths = anat_crumb.ls('subject_id', make_crumbs=False)
    >>> print(subj_paths)
    ["/home/hansel/data/raw/0040000/{session_id}/{image_type}/{image}",
     "/home/hansel/data/raw/0040001/{session_id}/{image_type}/{image}",
     "/home/hansel/data/raw/0040002/{session_id}/{image_type}/{image}",
     "/home/hansel/data/raw/0040003/{session_id}/{image_type}/{image}",
     "/home/hansel/data/raw/0040004/{session_id}/{image_type}/{image}",
     ...


If I want to know what are the existing ``subject_id``:

.. code:: python

    >>> subj_ids = crumb.ls('subject_id', fullpath=False)
    >>> print(subj_ids)
    ['0040000', '0040001', '0040002', '0040003', '0040004', '0040005', ...

or

.. code:: python

    >>> subj_ids = crumb['subject_id']
    >>> print(subj_ids)
    ['0040000', '0040001', '0040002', '0040003', '0040004', '0040005', ...

Now, if I wanted to get the path to all the images inside the ``anat_1`` folders,
I could do this:

.. code:: python

    >>> anat_crumb = crumb.replace(image_type='anat_1')
    >>> print(anat_crumb)
    /home/hansel/data/raw/{subject_id}/{session_id}/anat_1/{image}

or if I don't need to keep a copy of ``crumb``:

.. code:: python

    >>> crumb['image_type'] = 'anat_1'

    # get the paths to the images inside the anat_1 folders
    >>> anat_paths = crumb.ls('image')
    >>> print(anat_paths)
    [Crumb("/home/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz"),
     Crumb("/home/hansel/data/raw/0040004/session_1/anat_1/mprage.nii.gz"),
     ...

Remember that I can still access the replaced crumb arguments in each of the previous
crumbs in ``anat_paths``.

.. code:: python

    >>> subj_ids = [cr['subject_id'] for cr in anat_paths]
    >>> print(subj_ids)
    ['0040000', '0040001', '0040002', '0040003', '0040004', '0040005', ...

    >>> files = [cr['image'] for cr in anat_paths]
    >>> print(files)
    ['mprage.nii.gz', 'mprage.nii.gz', 'mprage.nii.gz', 'mprage.nii.gz', ...


More features and tricks
------------------------

There are more possibilities such as:

- creating folder trees with a value of maps for the crumbs:

    .. code:: python

        >>> from hansel import mktree, ParameterGrid

        >>> crumb = Crumb("/home/hansel/raw/{subject_id}/{session_id}/{modality}/{image}")

        >>> values_map = {'session_id': ['session_' + str(i) for i in range(2)],
        >>>               'subject_id': ['subj_' + str(i) for i in range(3)]}

        >>> mktree(crumb, list(ParameterGrid(values_map)))


- check the feasibility of a crumb path:

    .. code:: python

        >>> crumb = Crumb("/home/hansel/raw/{subject_id}/{session_id}/{modality}/{image}")

        # ask if there is any subject with the image 'lollipop.png'.
        >>> crumb['image'] = 'lollipop.png'
        >>> assert crumb.exists()


- check which subjects have 'jujube.png' and 'toffee.png' files:

    .. code:: python

        >>> crumb = Crumb("/home/hansel/raw/{subject_id}/{session_id}/{modality}/{image}")

        >>> toffee_crumb = crumb.replace(image='toffee.png')
        >>> jujube_crumb = crumb.replace(image='jujube.png')

        # using sets functionality
        >>> gluttons = set(toffee_crumb['subject_id']).intersection(set(jujube_crumb['subject_id'])
        >>> print(gluttons)
        ['gretel', 'hansel']


- unfold the whole crumb path to get the whole filetree in a list of paths:

    .. code:: python

        >>> all_images = Crumb("/home/hansel/raw/{subject_id}/{session_id}/{modality}/{image}")
        >>> all_images = crumb.unfold()
        >>> print(all_images)
        [Crumb("/home/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040000/session_1/rest_1/rest.nii.gz"),
         Crumb("/home/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040001/session_1/rest_1/rest.nii.gz"),
         Crumb("/home/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040002/session_1/rest_1/rest.nii.gz"),
         Crumb("/home/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040003/session_1/rest_1/rest.nii.gz"),
         ...

        # and you can ask for the value of the crumb argument in each element
        >>> print(crumbs[0]['subject_id'])
        0040000

- Use ``re.match`` or ``fnmatch`` expressions to filter the paths:

    The syntax for crumb arguments with a regular expression is: ``"{<arg_name>:<reg_regex>}"``

    .. code:: python

        # only the session_0 folders
        >>> s0_imgs = Crumb("/home/hansel/raw/{subject_id}/{session_id:*_0}/{modality}/{image}")
        >>> s0_imgs = crumb.unfold()
        >>> print(s0_imgs)
        [Crumb("/home/hansel/data/raw/0040000/session_0/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040000/session_0/rest_1/rest.nii.gz"),
         Crumb("/home/hansel/data/raw/0040001/session_0/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040001/session_0/rest_1/rest.nii.gz"),
         ...

    The default is for ``fnmatch`` expressions. If you prefer using ``re.match`` for filtering,
    set the ``regex`` argument to ``'re'`` in the constructor.

    .. code:: python

        # only the ``session_0`` folders
        >>> s0_imgs = Crumb("/home/hansel/raw/{subject_id}/{session_id:^.*_0$}/{modality}/{image}",
        >>>                 regex='re')
        >>> s0_imgs = crumb.unfold()
        >>> print(s0_imgs)
        [Crumb("/home/hansel/data/raw/0040000/session_0/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040000/session_0/rest_1/rest.nii.gz"),
         Crumb("/home/hansel/data/raw/0040001/session_0/anat_1/mprage.nii.gz"),
         Crumb("/home/hansel/data/raw/0040001/session_0/rest_1/rest.nii.gz"),
         ...


More functionalities, ideas and comments are welcome.


Dependencies
============

Please see the requirements.txt file. Before installing this package,
install its dependencies with:

    .. code:: bash

        pip install -r requirements.txt


Install
=======

It works on Python 3.4, 3.5 and 2.7. For Python 2.7 install `pathlib2` as well.

This package uses setuptools. You can install it running:

    .. code:: bash

        python setup.py install


If you already have the dependencies listed in requirements.txt
installed, to install in your home directory, use:

    .. code:: bash

        python setup.py install --user

To install for all users on Unix/Linux:

    .. code:: bash

        python setup.py build
        sudo python setup.py install


You can also install it in development mode with:

    .. code:: bash

        python setup.py develop


Development
===========

Code
----

Github
~~~~~~

You can check the latest sources with the command:

    .. code:: bash

        git clone https://www.github.com/alexsavio/hansel.git


or if you have write privileges:

    .. code:: bash

        git clone git@github.com:alexsavio/hansel.git


If you are going to create patches for this project, create a branch
for it from the master branch.

We tag stable releases in the repository with the version number.

Testing
-------

We are using `py.test <http://pytest.org/>`__ to help us with the testing.

Otherwise you can run the tests executing:

    .. code:: bash

        python setup.py test

or

    .. code:: bash

        py.test

or

    .. code:: bash

        make test


.. |PyPI| image:: https://img.shields.io/pypi/v/hansel.svg
        :target: https://pypi.python.org/pypi/hansel

.. |Build Status| image:: https://travis-ci.org/alexsavio/hansel.svg?branch=master
   :target: https://travis-ci.org/alexsavio/hansel

.. |Coverage Status| image:: https://coveralls.io/repos/alexsavio/hansel/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/alexsavio/hansel?branch=master

.. |PyPI Downloads| image:: https://img.shields.io/pypi/dm/hansel.svg
        :target: https://pypi.python.org/pypi/hansel

.. |Code Health| image:: https://landscape.io/github/alexsavio/hansel/master/landscape.svg?style=flat
        :target: https://landscape.io/github/alexsavio/hansel/master
        :alt: Code Health

.. |Scrutinizer| image:: https://img.shields.io/scrutinizer/g/alexsavio/hansel.svg
        :target: https://scrutinizer-ci.com/g/alexsavio/hansel/?branch=master
        :alt: Scrutinizer Code Quality

