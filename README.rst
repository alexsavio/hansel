hansel
======

Parametric file paths to access and build structured folder trees.

|PyPI| |Build Status| |Coverage Status| |Code Health|

It almost doesn't have `Dependencies`_, check how to `Install`_ it.

Github repository: https://github.com/alexsavio/hansel

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

    >>> from pprint import pprint
    >>> from hansel import Crumb

    # create the crumb
    >>> crumb = Crumb("{base_dir}/raw/{subject_id}/{session_id}/{image_type}/{image}")

    # set the base_dir path
    >>> crumb = crumb.replace(base_dir='/tmp/hansel/data')
    >>> print(str(crumb))
    /tmp/hansel/data/raw/{subject_id}/{session_id}/{image_type}/{image}

    # get the ids of the subjects
    >>> subj_ids = crumb['subject_id']
    >>> print(subj_ids)
    ['0040000', '0040001', '0040002', '0040003', '0040004', '0040005', ...

    # get the paths to the subject folders, the output can be strings or crumbs,
    # you choose with the ``make_crumbs`` boolean argument. Default: True.
    >>> subj_paths = crumb.ls('subject_id', make_crumbs=True)
    >>> pprint(subj_paths)
    [Crumb("/tmp/hansel/data/raw/0040000/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040001/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040002/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040003/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040004/{session_id}/{image_type}/{image}"),
     ...

    # set the image_type
    >>> anat_crumb = crumb.replace(image_type='anat_1')
    >>> print(anat_crumb)
    /tmp/hansel/data/raw/{subject_id}/{session_id}/anat_1/{image}

    # get the paths to the images inside the anat_1 folders
    >>> anat_paths = anat_crumb.ls('image')
    >>> pprint(anat_paths)
    [Crumb("/tmp/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040004/session_1/anat_1/mprage.nii.gz"),
     ...

    # get the ``session_id`` of each of these ``anat_paths``
    >>> sessions = [cr['session_id'][0] for cr in anat_paths]
    >>> print(sessions)
    ['session_1', 'session_1', 'session_1', 'session_1', 'session_1', ...

    # if you don't want the the output to be ``Crumbs`` but string paths:
    >>> anat_paths = anat_crumb.ls('image', make_crumbs=False)
    >>> pprint(anat_paths)
    ['/tmp/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz',
     '/tmp/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz',
     '/tmp/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz',
     '/tmp/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz',
     '/tmp/hansel/data/raw/0040004/session_1/anat_1/mprage.nii.gz',
     ...

    # you can also use a list of ``fnmatch`` expressions to ignore certain files patterns
    # using the ``ignore_list`` argument in the constructor.
    # For example, the files that start with '.'.
    >>> crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}/{image}", ignore_list=['.*'])

Once you have a fully defined Crumb, you can use its ``path`` for operations with the corresponding file.
For that you have to convert it to string by using ``str(crumb)`` or ``crumb.path``.

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
    /home/hansel/data/raw/{subject_id}/{session_id}/{image_type}/{image}

if I don't need a copy of ``crumb``, I can use the ``[]`` operator:

.. code:: python

    >>> crumb['base_dir'] = '/tmp/hansel'
    >>> print(str(crumb))
    /tmp/hansel/data/raw/{subject_id}/{session_id}/{image_type}/{image}

Now that the root path of my dataset is set, I can start querying my
crumb path.

If I want to know the path to the existing ``subject_id`` folders:

We can use the ``ls`` function. Its output can be ``str`` or ``Crumb``.
I can choose this using the ``make_crumbs`` argument (default: True):

.. code:: python

    >>> subj_crumbs = crumb.ls('subject_id')
    >>> pprint(subj_crumbs)
    [Crumb("/tmp/hansel/data/raw/0040000/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040001/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040002/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040003/{session_id}/{image_type}/{image}"),
     Crumb("/tmp/hansel/data/raw/0040004/{session_id}/{image_type}/{image}"),
     ...

    >>> subj_paths = crumb.ls('subject_id', make_crumbs=False)
    >>> pprint(subj_paths)
    ['/tmp/hansel/data/raw/0040000/{session_id}/{image_type}/{image}',
     '/tmp/hansel/data/raw/0040001/{session_id}/{image_type}/{image}',
     '/tmp/hansel/data/raw/0040002/{session_id}/{image_type}/{image}',
     '/tmp/hansel/data/raw/0040003/{session_id}/{image_type}/{image}',
     '/tmp/hansel/data/raw/0040004/{session_id}/{image_type}/{image}',
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
    /tmp/hansel/data/raw/{subject_id}/{session_id}/anat_1/{image}

or if I don't need to keep a copy of ``crumb``:

.. code:: python

    >>> crumb['image_type'] = 'anat_1'

    # get the paths to the images inside the anat_1 folders
    >>> anat_paths = crumb.ls('image')
    >>> pprint(anat_paths)
    [Crumb("/tmp/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz"),
     Crumb("/tmp/hansel/data/raw/0040004/session_1/anat_1/mprage.nii.gz"),
     ...

Remember that I can still access the replaced crumb arguments in each of the previous
crumbs in ``anat_paths``.

.. code:: python

    >>> subj_ids = [cr['subject_id'][0] for cr in anat_paths]
    >>> print(subj_ids)
    ['0040000', '0040001', '0040002', '0040003', '0040004', ...

    >>> files = [cr['image'][0] for cr in anat_paths]
    >>> print(files)
    ['mprage.nii.gz', 'mprage.nii.gz', 'mprage.nii.gz', 'mprage.nii.gz', ...


More features and tricks
------------------------

There are more possibilities such as:

Creating folder trees
~~~~~~~~~~~~~~~~~~~~~

Use `mktree` and `ParameterGrid` to create a tree of folders.

    .. code:: python

        >>> from hansel import mktree
        >>> from hansel.utils import ParameterGrid

        >>> crumb = Crumb("/tmp/hansel/data/raw/{subject_id}/{session_id}/{image_type}/{image}")

        >>> session_ids = ["session_{}".format(i) for i in range(2)]
        >>> subject_ids = ["subj_{}".format(i) for i in range(3)]

        >>> values_map = dict(session_id=session_ids, subject_id=subject_ids)

        >>> crumbs = mktree(crumb, list(ParameterGrid(values_map)))
        >>> pprint(crumbs)
        [Crumb("/tmp/hansel/data/raw/subj_0/session_0/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/raw/subj_1/session_0/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/raw/subj_2/session_0/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/raw/subj_0/session_1/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/raw/subj_1/session_1/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/raw/subj_2/session_1/{image_type}/{image}")]


Check the feasibility of a crumb path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code:: python

        >>> crumb = Crumb("/tmp/hansel/raw/{subject_id}/{session_id}/{image_type}/{image}")

        # ask if there is any subject with the image 'lollipop.png'.
        >>> crumb['image'] = 'lollipop.png'
        >>> assert not crumb.exists()


Check which subjects have 'jujube.png' and 'toffee.png' files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code:: python

        >>> crumb = Crumb("/tmp/hansel/raw/{subject_id}/{session_id}/{image_type}/{image}")

        >>> toffee_crumb = crumb.replace(image='toffee.png')
        >>> jujube_crumb = crumb.replace(image='jujube.png')

        # using sets functionality
        >>> gluttons = set(toffee_crumb['subject_id']).intersection(set(jujube_crumb['subject_id']) # doctest: +SKIP
        >>> print(gluttons)  # doctest: +SKIP
        ['gretel', 'hansel']


Use the `intersection` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use it for comparisons on more than one crumb argument.
This can be used to compare datasets with the same structure in different folders.

*One argument*

Imagine that we have two working folders of subjects for two different projects: `proj1` and `proj2`.
If I want to check what subjects are common to both projects:

    .. code:: python

        >>> from hansel import intersection

        # using one argument
        >>> cr_proj1 = Crumb("/tmp/hansel/data/proj1/{subject_id}/{session_id}/{image_type}/{image}")
        >>> cr_proj2 = Crumb("/tmp/hansel/data/proj2/{subject_id}/{session_id}/{image_type}/{image}")

        # set the `on` argument in `intersection` to specify which crumb arguments to merge.
        >>> merged = intersection(cr_proj1, cr_proj2, on=['subject_id'])
        >>> pprint(merged)
        [(('subject_id', '0040006'),),
         (('subject_id', '0040007'),),
         (('subject_id', '0040008'),),
         (('subject_id', '0040009'),)]

        # I can pick these subject crumbs from this result using the `build_paths` function.
        >>> proj1_merged_paths = cr_proj1.build_paths(merged, make_crumbs=True)
        >>> type(proj1_merged_paths)
        <class 'generator'>

        >>> pprint(list(proj1_merged_paths))
        [Crumb("/tmp/hansel/data/proj1/0040006/{session_id}/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/proj1/0040007/{session_id}/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/proj1/0040008/{session_id}/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/proj1/0040009/{session_id}/{image_type}/{image}")]

        >>> pprint(list(cr_proj2.build_paths(merged, make_crumbs=True)))
        [Crumb("/tmp/hansel/data/proj2/0040006/{session_id}/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/proj2/0040007/{session_id}/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/proj2/0040008/{session_id}/{image_type}/{image}"),
         Crumb("/tmp/hansel/data/proj2/0040009/{session_id}/{image_type}/{image}")]


*Two arguments*

Now, imagine that I have different sets of `{image}` for these subjects.
I want to check which of those subjects have exactly the same images.
Let's say that the subject `0040000` has a `anatomical.nii.gz` instead of `mprage.nii.gz`.

    .. code:: python

        >>> from hansel import intersection

        # using one argument
        >>> cr_proj3 = Crumb("/tmp/hansel/data/proj3/{subject_id}/{session_id}/anat_1/{image}")
        >>> cr_proj4 = Crumb("/tmp/hansel/data/proj4/{subject_id}/{session_id}/anat_1/{image}")

        # set the `on` argument in `intersection` to specify which crumb arguments to merge.
        >>> merged = intersection(cr_proj3, cr_proj4, on=['subject_id', 'image'])
        >>> pprint(merged)
        [(('subject_id', '0040001'), ('image', 'mprage.nii.gz')),
         (('subject_id', '0040002'), ('image', 'mprage.nii.gz')),
         (('subject_id', '0040003'), ('image', 'mprage.nii.gz')),
         (('subject_id', '0040004'), ('image', 'mprage.nii.gz')),
        ...

        # I can pick these image crumbs from this result using the `build_paths` function.
        >>> pprint(list(cr_proj3.build_paths(merged, make_crumbs=True)))
        [Crumb("/tmp/hansel/data/proj3/0040001/{session_id}/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/proj3/0040002/{session_id}/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/proj3/0040003/{session_id}/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/proj3/0040004/{session_id}/anat_1/mprage.nii.gz"),
         ...

        >>> pprint(list(cr_proj4.build_paths(merged, make_crumbs=True)))
        [Crumb("/tmp/hansel/data/proj4/0040001/{session_id}/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/proj4/0040002/{session_id}/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/proj4/0040003/{session_id}/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/proj4/0040004/{session_id}/anat_1/mprage.nii.gz"),
        ...

        # adding 'mod' to the intersection would be:
        >>> common_values = intersection(cr_proj3, cr_proj4, on=['subject_id', 'session_id', 'image'])
        >>> pprint(common_values, width=120)
        [(('subject_id', '0040001'), ('session_id', 'session_1'), ('image', 'mprage.nii.gz')),
         (('subject_id', '0040002'), ('session_id', 'session_1'), ('image', 'mprage.nii.gz')),
         (('subject_id', '0040003'), ('session_id', 'session_1'), ('image', 'mprage.nii.gz')),
         (('subject_id', '0040004'), ('session_id', 'session_1'), ('image', 'mprage.nii.gz')),
         ...


The `unfold` and `ls` functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unfold the whole crumb path to get the whole file tree in a list of paths:

    .. code:: python

        >>> all_images = Crumb("/tmp/hansel/data/raw/{subject_id}/{session_id}/{image_type}/{image}")
        >>> all_images = all_images.unfold()
        >>> pprint(all_images)
        [Crumb("/tmp/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040000/session_1/rest_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040001/session_1/rest_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040002/session_1/rest_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040003/session_1/anat_1/mprage.nii.gz"),
        ...

        # and you can ask for the value of the crumb argument in each element
        >>> print(all_images[0]['subject_id'])
        ['0040000']

Note that `unfold` is the same as calling `ls` function without arguments.


Use regular expressions
~~~~~~~~~~~~~~~~~~~~~~~

Use ``re.match`` or ``fnmatch`` expressions to filter the paths:

The syntax for crumb arguments with a regular expression is: ``"{<arg_name>:<arg_regex>}"``

    .. code:: python

        # only the session_1 folders
        >>> session1_cr = Crumb("/tmp/hansel/data/raw/{subject_id}/{session_id:*_1}/{image_type}/{image}")
        >>> session1_imgs = session1_cr.ls()
        >>> pprint(session1_imgs)
        [Crumb("/tmp/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040000/session_1/rest_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040001/session_1/rest_1/mprage.nii.gz"),
        ...

The default is for ``fnmatch`` expressions. If you prefer using ``re.match`` for filtering,
set the ``regex`` argument to ``'re'`` or ``'re.ignorecase'`` in the constructor.

    .. code:: python

        # only the rest images from the subject ``040000``
        >>> s0_rest_cr = Crumb("/tmp/hansel/data/raw/{subject_id:.*00$}/{session_id}/{image_type:rest.*}/{image}", regex='re')
        >>> s0_rest_imgs = s0_rest_cr.ls()
        >>> print(s0_rest_imgs)
        [Crumb("/tmp/hansel/data/raw/0040000/session_1/rest_1/mprage.nii.gz")]

The regular expressions can be checked with the `patterns` property.

    .. code:: python

        >>> pprint(s0_rest_cr.patterns)
        {'image_type': 'rest.*', 'subject_id': '.*00$'}

And can be also modified with the `set_pattern` function.

    .. code:: python

        >>> s0_rest_cr.set_pattern('session_id', '.*_1$')
        >>> pprint(s0_rest_cr.patterns)
        {'image_type': 'rest.*', 'session_id': '.*_1$', 'subject_id': '.*00$'}
        >>> s0_rest_cr.path
        '/tmp/hansel/data/raw/{subject_id:.*00$}/{session_id:.*_1$}/{image_type:rest.*}/{image}'


A regular expression can be temporarily set with the `ls` function and the `[]`
operator.

    .. code:: python

        >>> crumb = Crumb("/tmp/hansel/data/raw/{subject_id}/{session_id}/{image_type}/{image}")
        >>> mprage_crumb = crumb.ls('image:mprage.*')
        >>> pprint(mprage_crumb)
        [Crumb("/tmp/hansel/data/raw/0040000/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040000/session_1/rest_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040001/session_1/anat_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040001/session_1/rest_1/mprage.nii.gz"),
         Crumb("/tmp/hansel/data/raw/0040002/session_1/anat_1/mprage.nii.gz"),
        ...

        >>> pprint(crumb['image:mprage.*'])
        ['mprage.nii.gz',
         'mprage.nii.gz',
         'mprage.nii.gz',
         'mprage.nii.gz',
         'mprage.nii.gz',
         'mprage.nii.gz',
        ...


Copy and modify folder structure with `crumb_copy`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy a folder structure from one crumb to the other. The source crumb
must be fully specified, i.e., all crumb arguments must get an existing value.
In addition the destination crumb can only have a subset of the crumb arguments
of the source crumb.

    .. code:: python

        >>> from hansel import Crumb, crumb_copy
        >>> src_cr = Crumb("/tmp/hansel/data/raw/{subj_id}/{sess}/{type}/{img}")
        >>> dst_cr = Crumb("/tmp/hansel/data/copy/{subj_id}/{sess}/{type}")
        >>> crumb_copy(src_cr, dst_cr)


More functionalities, ideas and comments are welcome.


Command Line
============

`hansel` will install a command called `crumb`.
This CLI has been made with `Click <http://click.pocoo.org/>`__,
so try `crumb -h` to see more details.

You can use `Crumb.ls`:

    .. code:: bash

        crumb ls "/data/hansel/cobre/{sid:4*100}/{session}/{img}"


Copy one file tree to another file tree with `crumb copy`:

    .. code:: bash

        crumb copy "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"


Link one file tree to another file tree with `link`:

    .. code:: bash

        crumb link "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"


Return the intersection between crumb1 and crumb2 on a given argument with the `intersect` function:

    .. code:: bash

        crumb intersect --on "sid" "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"


Return the difference `crumb1 - crumb2` on a given argument with the `diff` function:

    .. code:: bash

        crumb diff --on "sid" "/data/hansel/cobre/{sid}/{session}/{img}" "/data/hansel/cobre2/{sid}/{img}"


Dependencies
============

Please see the requirements.txt file. Before installing this package,
install its dependencies with:

    .. code:: bash

        pip install -r requirements.txt


Install
=======

It works on Python 3.4, 3.5 and 2.7. For Python 2.7 install `pathlib2` as well.

    .. code:: bash

        pip install hansel


From sources
------------

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

.. |Code Health| image:: https://landscape.io/github/alexsavio/hansel/master/landscape.svg?style=flat
        :target: https://landscape.io/github/alexsavio/hansel/master
        :alt: Code Health
