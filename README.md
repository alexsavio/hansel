hansel
======

Flexible parametric file paths to make queries, build folder trees and
smart folder structure access.

[![image](https://travis-ci.org/alexsavio/hansel.svg?branch=master)](https://travis-ci.org/alexsavio/hansel)

[![image](https://coveralls.io/repos/alexsavio/hansel/badge.svg?branch=master&service=github)](https://coveralls.io/github/alexsavio/hansel?branch=master)

Usage
=====

Quick Intro
-----------

```python
from hansel import Crumb

crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}")

crumb = crumb.replace('base_dir', '/home/hansel')

assert str(crumb) == "/home/hansel/data/raw/{subject_id}/{session_id}/{image_type}"


anat_crumb = crumb2.replace(modality='anat')

subjec_paths_crumbs = anat_crumb.ls('subject_id')


subject_ids = crumb.ls('subject_id', fullpath=False)

assert subject_ids == ['0040000', '0040001', '0040002', '0040003', '0040004', ....]


anat_crumb = crumb.replace(image_type='anat_1')

anat_paths = anat_crumb.ls('image')
```


Long Intro
----------

I often find myself in a work related with structured folder paths. For
example:

```
cobre
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

```

I have tried many ways of "modelling" these situations: loops,
dictionaries, configuration files, etc. I always end up doing a
different thing for the same problem over and over again.

This week I grew tired of it and decided to make a representation of a
structured folder tree in a string and access it the most easy way.

If you look at the folder structure above I have: the root directory
from where it is hanging, then I have an identifier (in this case a
subject identification), then a session identification and a data type
(in this case an image type).

With hansel I can represent the folder structure like this:

```python
from hansel import Crumb

crumb = Crumb("{base_dir}/data/raw/{subject_id}/{session_id}/{image_type}")
```

Let's say we have the structure above hanging from a base directory like
`/home/hansel/`.

I can use the `replace` function to make set the `base_dir` parameter:

```python
crumb = crumb.replace('base_dir', '/home/hansel')

assert str(crumb) == "/home/hansel/data/raw/{subject_id}/{session_id}/{image_type}"
```

Now that the root path of my dataset is set, I can start querying my crumb path.

If I want to know the path to the existing `subject_ids` folders:

```python
subject_paths = anat_crumb.ls('subject_id')
```

If I want to know what are the existing `subject_ids`:

```python
subject_ids = crumb.ls('subject_id', fullpath=False)
```

Now, if I wanted to get the path to all the `anat_1` images, I could do this:

```python
anat_crumb = crumb.replace(image_type='anat_1')

anat_paths = anat_crumb.ls('image')
```

More functionalities, ideas and comments are welcome.
I am working on a few improvemens, such as calling `replace` from `__setitem__`
and `ls` from `__getitem__`.

Dependencies
============

Please see the requirements.txt file. Before installing this package,
install its dependencies with:

> pip install -r requirements.txt

Install
=======

This package uses setuptools. You can install it running:

> python setup.py install

If you already have the dependencies listed in requirements.txt
installed, to install in your home directory, use:

    python setup.py install --user

To install for all users on Unix/Linux:

    python setup.py build
    sudo python setup.py install

You can also install it in development mode with:

    python setup.py develop

Development
===========

Code
----

### Github

You can check the latest sources with the command:

    git clone https://www.github.com/alexsavio/hansel.git

or if you have write privileges:

    git clone git@github.com:alexsavio/hansel.git

If you are going to create patches for this project, create a branch for
it from the master branch.

We tag stable releases in the repository with the version number.

Testing
-------

We are using [py.test](http://pytest.org/) to help us with the testing.
If you don't have pytest installed you can run the tests using:

> ./runtests.py

Otherwise you can run the tests executing:

> python setup.py test

or

> pytest
