import inspect
import sys

__version__ = "13.0.0"


def get_all(name, objects_to_skip=None, skip_private=True):
    """Return a list of all functions and classes in a module
    up to the point in the module when this is called.

    Can be used to populate the __all__ field of a module,
    which sets the objects to be included when importing the
    calling module via e.g. `from <module> import *`

    Parameters
    ----------
    name : str
        The `__name__` attribute of the calling module.
        (See example below)
    objects_to_skip : list of strings
        A list of object names to not include when
        forming the list.
        Defaults to None.
    skip_private : bool
        True to skip including objects whose name
        begins with an underscore, e.g. `_my_private_foo`.
        False to include private objects.
        Defaults to True.

    Example
    -------

    To import all from my_module.py into this __init__.py
    file like this:
        `from my_module import *`
    we need to set the `__all__` variable in `my_module.py`
    to avoid reimporting all of objects from that module's
    import statements (e.g. numpy, etc.).

    Example my_module.py:

    from dataclasses import dataclass
    import nisarqa

    # Immediately following the import statements,
    # get the list of currently-available objects.
    # We do not want to import these objects from outside
    # codebases.
    # Note: `__name__` is the module attribute; there
    # are no quote marks.
    objects_to_skip = nisarqa.get_all(__name__)
    #    Will set `objects_to_skip` equal to ['dataclass']

    @dataclass
    class MyDataClass:
        item1: str
        item2: str

    def my_func():
        pass

    def _my_private_foo():
        pass

    # Call `get_all()` again at the very end of the module
    # to include all functions and classes created during
    # the module.
    __all__ = nisarqa.get_all(__name__, objects_to_skip=objects_to_skip)
    #    __all__ will be set equal to ['MyDataClass', 'my_func']

    # Alternatively, could include private functions:
    __all__ = nisarqa.get_all(__name__, skip_private=False)
    #    __all__ will be set equal to ['MyDataClass', '_my_private_foo', 'dataclass', 'my_func']
    """

    # Get all objects from the calling code
    item_list = [
        name
        for name, obj in inspect.getmembers(sys.modules[name])
        if (inspect.isfunction(obj) or inspect.isclass(obj))
    ]

    if objects_to_skip is not None:
        item_list = [x for x in item_list if (x not in objects_to_skip)]

    # Remove objects that start with an underscore
    if skip_private:
        item_list = [x for x in item_list if not x.startswith("_")]

    return item_list


# import constants and utilities into the global namespace
# These will be accessed by all products. Note that each
# function name will need to be unique across the submodules.
# WARNING: If adding a new module to this list,
# make sure to set the `__all__` attribute
# within that new module.
# A helper function to set `__all__` (with example) can be found above.
# Note: Keep each NISAR product in a unique namespace, due to a higher
# potential for overlapping function names

# Import Globals first (these must be imported before the parameters)
from .globals import *
from .stats_h5_globals import *

# Next import parameters, products, utils, etc.
from .parameters import *
from .utils import *
from .products import *
from .validate import *
from .processing import *
