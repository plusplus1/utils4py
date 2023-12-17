#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["init_registry"]

import copy
import inspect
import logging

import click.core

from utils4py.scan import walk_modules as scan_package_modules
from ._base import BaseHandler, name_of

_inited = False


def init_registry(cli: click.Group, base_packages, **startup_kwargs):
    """
    init handler registry
    """

    global _inited
    if _inited:
        return

    _inited = True

    assert isinstance(cli, click.core.Group)

    exclude_module = {BaseHandler.__module__}
    param_field = '__click_params__'
    register_map = dict()

    def _convert_handler_to_command(handler_clz, **copy_startup_kwargs):

        def _command(context, *args, **kwargs):
            # init handler instance and execute handler
            handler_instance = handler_clz(ctx=context, **copy_startup_kwargs)  # type: BaseHandler
            handler_instance.handle(*args, **kwargs)  # pass through click args and kwargs

        return _command

    for implement_package in base_packages:

        for handle_module in scan_package_modules(implement_package):

            for var_name in vars(handle_module):
                try:
                    handler_clz_define = getattr(handle_module, var_name)
                    assert handler_clz_define and inspect.isclass(handler_clz_define) and issubclass(handler_clz_define, BaseHandler)
                    assert handler_clz_define.__module__ not in exclude_module
                    command_name = name_of(handler_clz_define)
                    assert command_name
                    command_location = "%s.%s" % (handler_clz_define.__module__, handler_clz_define.__name__)
                except AssertionError:
                    continue

                if command_name in register_map:
                    raise Exception("name duplicated handler, %s , %s", command_name, command_location)

                command_help_str = handler_clz_define.__doc__.strip()
                command_func = click.pass_context(_convert_handler_to_command(handler_clz_define, **copy.deepcopy(startup_kwargs)))

                # copy handler click params to command
                setattr(command_func, param_field, getattr(handler_clz_define, param_field, None))

                register_map[command_name] = command_func

                # bind command to click group
                cli.command(name=command_name, help=command_help_str)(command_func)

                logging.debug("[register handler]\t\t%s -> %s, %s", command_name, command_location, command_help_str)
            pass
        pass

    return
