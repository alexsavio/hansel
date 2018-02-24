import os
import re


def import_pyfile(pathname, mod_name=''):
    """Import the contents of filepath as a Python module.
    Parameters
    ----------
    pathname: str
        Path to the .py file to be imported as a module
    mod_name: str
        Name of the module when imported

    Returns
    -------
    mod:
        The imported module

    Raises
    ------
    IOError:
        If file is not found
    """
    if not os.path.isfile(pathname):
        raise FileNotFoundError('File {0} not found.'.format(pathname))

    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader('', pathname)
    mod = loader.load_module(mod_name)
    return mod


def test_version():
    mod = import_pyfile('hansel/version.py')

    assert isinstance(mod.__version__, str)
    assert re.match(r'[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}', mod.__version__)
    assert all(isinstance(val, int) for val in mod.VERSION)
