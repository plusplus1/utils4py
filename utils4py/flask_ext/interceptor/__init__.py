#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import inspect
import logging

import flask
import six

import utils4py.scan

_logger = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseInterceptor(object):
    """
        Define base request interceptor
    """

    def __init__(self, app, **kwargs):
        """
        :param flask.Flask app:
        """
        self.app = app
        self.logger = kwargs.get('logger') or _logger

        pass

    def before_request(self, *args, **kwargs):
        """
        Execute after received a request and before business logic function,
        auto decorated with Flask app's `before_request`.

        This function will be called without any arguments. If it returns a
        non-None value, the value is handled as if it was the return value from
        the view, and further request handling is stopped.
        """
        pass

    def after_request(self, *args, **kwargs):
        """
        Execute at the end of request regardless of whether there was an exception or not,
        auto decorated with Flask app's `teardown_request`

        Generally this function must take every necessary step to avoid
        that they will fail.  If they do execute code that might fail they
        will have to surround the execution of these code by try/except
        statements and log occurring errors.

        When this function was called because of an exception it will
        be passed an error object.

        The return values are ignored.
        """
        pass

    # def before_response(self, resp):
    #     """
    #     Register a function to be run after each request.
    #     Your function must take one parameter, an instance of
    #     :attr:`response_class` and return a new response object or the
    #     same (see :meth:`process_response`).
    #     """
    #     return resp

    def __call__(self, *args, **kwargs):
        self.app.before_request(self.before_request)
        self.app.teardown_request(self.after_request)

        before_response = getattr(self, 'before_response', None)
        if before_response and callable(before_response):
            self.app.after_request(before_response)

        return

    pass


def _scan_usable_interceptors(path):
    usable_filters = []
    for a_module in utils4py.scan.walk_modules(path):  # type:module

        for attr_name in vars(a_module):  # type: str
            if attr_name.startswith('_') or not attr_name[0].isupper():
                continue

            filter_cls = getattr(a_module, attr_name, None)  # type: BaseInterceptor
            try:
                assert filter_cls, 'must not by empty'
                assert inspect.isclass(filter_cls), 'must be class'
                assert issubclass(filter_cls, BaseInterceptor), 'must be sub class of BaseFilter'
                assert filter_cls is not BaseInterceptor, 'must not be BaseFilter'
                assert filter_cls.__module__ == a_module.__name__, 'must be defined in this module'
                usable_filters.append(filter_cls)
            except AssertionError:
                continue
        pass

    return usable_filters


def init_interceptors(app, paths, **kwargs):
    """
    init filters

    :param flask.Flask app:
    :param list[str] paths:
    :return:
    """

    if not paths:
        return

    reg_map = dict()

    def _register_one_package(package):

        if not package:
            return

        usable_interceptors = _scan_usable_interceptors(package)
        if not usable_interceptors:
            return

        for interceptor_cls in usable_interceptors:
            cls_id = id(interceptor_cls)
            if cls_id in reg_map:
                continue

            interceptor_name = "{}.{}".format(interceptor_cls.__module__, interceptor_cls.__name__)
            interceptor_cls(app, **kwargs)()
            reg_map[id(interceptor_cls)] = interceptor_cls

            _logger.info("---> [Register interceptor] name = %-50s", interceptor_name)

        return

    for pkg in paths:
        _register_one_package(pkg)

    _logger.info("---> [Register interceptor] len = %s", len(reg_map))
    return


pass
