#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import logging
import re

import click
from werkzeug.utils import cached_property

import utils4py.conf

_logger = logging.getLogger(__name__)

__all__ = ["BaseHandler", "name", "name_of"]
__name_field = "__o_cmd_name"


class BaseHandler(object):
    """base handler """

    def __init__(self, **kwargs):
        self._logger = kwargs.get("logger") or _logger
        self._ctx = kwargs.get("ctx")
        pass

    @cached_property
    def logger(self) -> logging.Logger:
        return self._logger or _logger

    @cached_property
    def context(self) -> click.Context:
        return self._ctx

    @cached_property
    def pri_config(self) -> dict:
        return utils4py.conf.ConfUtils.load_yaml("handler/" + name_of(self.__class__) + ".yaml")

    @abc.abstractmethod
    def handle(self, *args, **kwargs):
        pass


def _get_name(f):
    if issubclass(f, BaseHandler):
        match = re.findall(r"[A-Z][a-z\d]+", f.__name__)
        if match:
            return "-".join(map(str.lower, filter(lambda x: x != "Handler", match)))
        else:
            return f.__name__

    return None


def name(**kwargs):
    _name = kwargs.get('name')

    def _wrap(f):
        if issubclass(f, BaseHandler):
            setattr(f, __name_field, _name or _get_name(f))

        return f

    return _wrap


def name_of(f):
    return getattr(f, __name_field, '') or _get_name(f)
