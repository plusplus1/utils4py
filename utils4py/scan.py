#!/usr/bin/env python
# -*- coding: utf-8 -*-


from importlib import import_module
from pkgutil import iter_modules


def walk_modules(path):
    """Loads a module and all its submodules from the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.
    """

    mods = []
    mod = import_module(path)
    mods.append(mod)
    if hasattr(mod, '__path__'):
        for _, sub_path, is_pkg in iter_modules(mod.__path__):
            full_path = path + '.' + sub_path
            if is_pkg:
                mods += walk_modules(full_path)
            else:
                sub_mod = import_module(full_path)
                mods.append(sub_mod)
    return mods
