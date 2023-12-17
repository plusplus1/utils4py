#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

import click.core

import utils4py.env
from ._base import BaseHandler, name
from ._registry import init_registry

__all__ = ["run", "BaseHandler", "name"]

_logger = logging.getLogger(__name__)

if utils4py.env.is_mac_os:
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'


@click.group(invoke_without_command=True)
@click.pass_context
def _cli_entry(ctx: click.Context, *args, **kwargs):
    not ctx.invoked_subcommand and print(ctx.get_help())
    return


def run(cmd_base_package, **kwargs):
    """
    scan command implementation and run command

    @param cmd_base_package: str or list[str] or tuple[str]
    """
    kwargs.setdefault('logger', _logger)
    init_registry(_cli_entry, [cmd_base_package] if isinstance(cmd_base_package, str) else cmd_base_package,
                  **kwargs)
    _cli_entry()
    pass
