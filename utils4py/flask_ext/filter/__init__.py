#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import inspect
import logging

import flask
import six
from six.moves import map, reduce

import utils4py.scan


@six.add_metaclass(abc.ABCMeta)
class BaseFilter(object):
    """
        define flask filter
    """

    def __init__(self, app, **kwargs):
        """
        :param flask.Flask app: 
        """
        self.app = app
        self.logger = kwargs.get('logger') or logging
        pass

    @abc.abstractmethod
    def before_request(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def after_request(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        self.app.before_request(self.before_request)
        self.app.teardown_request(self.after_request)

        before_response = getattr(self, 'before_response', None)
        if before_response and callable(before_response):
            self.app.after_request(before_response)

        return

    pass


def _scan_filters(path):
    filters = []
    for mod in utils4py.scan.walk_modules(path):
        if not hasattr(mod, 'Filter'):
            continue
        filter_cls = mod.Filter
        if not inspect.isclass(filter_cls) or not issubclass(filter_cls, BaseFilter) \
                or filter_cls is BaseFilter:
            continue
        filters.append(filter_cls)
        pass

    return filters


def init_filters(app, filters=None, paths=None, **kwargs):
    """
    init filters 

    :param flask.Flask app: 
    :param list filters: 
    :param list paths:
    :param kwargs: 
    :return: 
    """

    registered_map = dict()

    def _register(filter_classes):
        if not filter_classes:
            return
        for cls_filter in filter_classes:
            if not inspect.isclass(cls_filter) or not issubclass(cls_filter, BaseFilter) \
                    or cls_filter is BaseFilter:
                continue
            cls_id = id(cls_filter)
            if cls_id in registered_map:
                continue
            cls_filter(app, **kwargs)()
            str_name = "{}".format(cls_filter.__module__)
            logging.debug("\tRegistered Filter ok, name = %-50s", str_name)
            registered_map[id(cls_filter)] = cls_filter
        return

    _register(filters)

    if paths and isinstance(paths, list):
        other_filters = reduce(lambda x, y: x + y, map(_scan_filters, paths))
        _register(other_filters)

    logging.info("\tRegistered %d filters", len(registered_map))
    return
