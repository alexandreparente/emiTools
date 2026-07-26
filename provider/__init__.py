# -*- coding: utf-8 -*-

"""
Automatic discovery of QGIS Processing algorithms.

Every module placed inside this package is imported automatically, and any
class defined in it that subclasses QgsProcessingAlgorithm is collected by
discover_algorithm_classes() / discover_algorithms().

This means adding a new algorithm only requires creating a new .py file in
this folder with a QgsProcessingAlgorithm subclass inside it — there is no
manually maintained list of algorithms to keep in sync with
emi_tools_provider.py.

To keep an algorithm out of the registered list (e.g. work in progress),
prefix its file name with an underscore, e.g. "_emi_tools_wip_algorithm.py".
"""

import importlib
import inspect
import pkgutil

from qgis.core import QgsProcessingAlgorithm


def discover_algorithm_classes():
    """
    Import every (non-underscore-prefixed) module in this package and
    return every QgsProcessingAlgorithm subclass defined in them.
    """
    classes = []
    seen = set()

    for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
        if is_pkg or module_name.startswith("_"):
            continue

        module = importlib.import_module(f"{__name__}.{module_name}")

        for _, obj in inspect.getmembers(module, inspect.isclass):
            # Only collect classes actually defined in this module, not
            # ones imported for reuse (e.g. QgsProcessingAlgorithm itself,
            # or a base class shared between algorithms)
            if obj.__module__ != module.__name__:
                continue

            if obj is QgsProcessingAlgorithm:
                continue

            if not issubclass(obj, QgsProcessingAlgorithm):
                continue

            if obj in seen:
                continue

            seen.add(obj)
            classes.append(obj)

    return classes


def discover_algorithms():
    """
    Convenience helper that returns a fresh instance of every discovered
    algorithm class, ready to be passed to
    QgsProcessingProvider.addAlgorithm().
    """
    return [cls() for cls in discover_algorithm_classes()]
