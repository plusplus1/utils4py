#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import logging

import six
from flask import Flask, g, render_template

import utils4py
import utils4py.scan
import utils4py.service
from utils4py.service import ResultBuilder

__FIELD_FLAG_SERVICE_IMPL = "_flag_svr_impl"
__FIELD_ROUTE = "_route"
__FIELD_ENABLE = "_enable"
__FIELD_ENDPOINT = "_endpoint"
__FIELD_METHODS = "_methods"
__FIELD_TEMPLATE = "_template"


def service_route(**kwargs):
    _enable = kwargs.get("enable", True)
    _route = kwargs.get("route", "")
    _endpoint = kwargs.get("endpoint", "")
    _methods = kwargs.get("methods", None) or ['GET', 'POST']
    _template = kwargs.get("template", None)

    def _(cls):
        setattr(cls, __FIELD_FLAG_SERVICE_IMPL, True)
        setattr(cls, __FIELD_ENABLE, _enable)
        setattr(cls, __FIELD_ROUTE, _route)
        setattr(cls, __FIELD_ENDPOINT, _endpoint)
        setattr(cls, __FIELD_METHODS, _methods)
        if _template:
            setattr(cls, __FIELD_TEMPLATE, _template)
        return cls

    return _


class BaseService(utils4py.service.BaseService):
    """
        Flask base service 
    """

    KEY_HEADER_STATUS = "header_status"
    KEY_HEADER_MSG = "header_msg"
    KEY_TEMPLATE = "render_tpl"

    @classmethod
    def add_notice_log(cls, key, value):
        if not hasattr(g, 'kv_log'):
            g.kv_log = dict()
        g.kv_log[key] = value
        return

    pass


def _service_factory(cls):
    """
    
    :param type(BaseService) cls: 
    :return: 
    """

    def _do_response(result):

        header_status = result.get(cls.KEY_HEADER_STATUS, None)
        if header_status and isinstance(header_status, six.integer_types) and header_status != 200:
            header_msg = result.get(cls.KEY_HEADER_MSG, None) or ""
            return header_msg, header_status

        tpl = result.get(cls.KEY_TEMPLATE, None) or getattr(cls, __FIELD_TEMPLATE, None)
        if not tpl:
            return utils4py.TextUtils.json_dumps(result)

        return render_template(tpl, **result)

    def _(*args, **kwargs):
        obj = cls(*args, **kwargs)  # type: BaseService
        result = obj.execute(*args, **kwargs)

        try:
            code = result.get(ResultBuilder.KEY_ERROR_CODE)
            g.code = code
            if code != ResultBuilder.ERROR_CODE_OK:
                msg = result.get(ResultBuilder.KEY_ERROR_MESSAGE)
                if not hasattr(g, "kv_log") or not isinstance(g.kv_log, dict) or not g.kv_log.get("error", None):
                    obj.add_notice_log("error", msg)
        except (Exception,):
            pass

        return _do_response(result)

    return _


def _scan_services(path):
    svr_classes = []

    for mod in utils4py.scan.walk_modules(path):
        for s in dir(mod):
            if str.startswith(s, '_') or not str.isupper(s[0]):
                continue

            s_cls = getattr(mod, s)
            if not s_cls or not inspect.isclass(s_cls) or not issubclass(s_cls, BaseService) \
                    or s_cls is BaseService:
                continue

            if not getattr(s_cls, __FIELD_FLAG_SERVICE_IMPL, None):
                continue
            if not getattr(s_cls, __FIELD_ENABLE, False):
                continue

            str_route = getattr(s_cls, __FIELD_ROUTE, "")
            str_endpoint = getattr(s_cls, __FIELD_ENDPOINT, "")
            default_endpoint = "{}.{}".format(s_cls.__module__, s_cls.__name__)

            if not str_route:
                str_route = default_endpoint.replace(path, "", 1)
                str_route = "/" + "/".join(filter(lambda x: x, str.split(str_route, "."))[:-1])
                setattr(s_cls, __FIELD_ROUTE, str_route)
                pass

            if not str_endpoint:
                setattr(s_cls, __FIELD_ENDPOINT, default_endpoint)

            svr_classes.append(s_cls)
        pass

    return svr_classes


def init_routes(app, paths):
    """
    :param Flask app: 
    :param list paths: 
    :return: 
    """
    registered_map = dict()

    def _register(path):
        classes = _scan_services(path)
        if not classes or not isinstance(classes, list):
            return

        for s_cls in classes:
            if not s_cls or not inspect.isclass(s_cls) or not issubclass(s_cls, BaseService) \
                    or s_cls is BaseService:
                continue

            if not getattr(s_cls, __FIELD_FLAG_SERVICE_IMPL, None):
                continue
            if not getattr(s_cls, __FIELD_ENABLE, False):
                continue
            if id(s_cls) in registered_map:
                continue

            str_route = getattr(s_cls, __FIELD_ROUTE)
            str_endpoint = getattr(s_cls, __FIELD_ENDPOINT)
            methods = getattr(s_cls, __FIELD_METHODS)

            app.route(str_route, endpoint=str_endpoint, methods=methods)(_service_factory(s_cls))

            logging.debug("\tRegister Service ok, route = %-35s , endpoint=%s ", str_route, str_endpoint)
            registered_map[id(s_cls)] = s_cls
            pass

        return

    if paths and isinstance(paths, list):
        map(_register, paths)

    logging.info("\tRegistered %d services", len(registered_map))
    return


pass
