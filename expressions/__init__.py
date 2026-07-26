# -*- coding: utf-8 -*-

"""
Automatic discovery of QGIS expression functions.

Every module placed inside this package is imported automatically, and any
object created by the @qgsfunction decorator (an instance of
QgsExpressionFunction) is collected by discover_functions().

This means adding a new expression only requires creating a new .py file in
this folder with a @qgsfunction-decorated function inside it — there is no
manually maintained list of functions to keep in sync with emi_tools.py.

Modules whose file name starts with an underscore (e.g. "_sensor_data.py")
are treated as private helpers shared between expression files (e.g. logic
or lookup tables reused by more than one expression) and are imported as
regular Python modules, but are not scanned for expression functions.
"""

import importlib
import pkgutil

from qgis.core import QgsExpressionFunction


def discover_functions():
    """
    Import every (non-underscore-prefixed) module in this package and
    return every QGIS expression function found in them (i.e. objects
    created with @qgsfunction).
    """
    functions = []
    seen_ids = set()

    for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
        if is_pkg or module_name.startswith("_"):
            continue

        module = importlib.import_module(f"{__name__}.{module_name}")

        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue

            obj = getattr(module, attr_name)

            # Only collect actual QGIS expression functions, i.e. objects
            # produced by the @qgsfunction decorator
            if not isinstance(obj, QgsExpressionFunction):
                continue

            # Avoid duplicates if the same function object is re-exported
            # by more than one module (e.g. re-imported for convenience)
            if id(obj) in seen_ids:
                continue

            seen_ids.add(id(obj))
            functions.append(obj)

    return functions
