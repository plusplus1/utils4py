#!/usr/bin/env python
# -*- coding: utf-8 -*-


import abc
import inspect
import logging
import traceback

import flask
import six
from werkzeug.wrappers import BaseResponse

import utils4py.env
import utils4py.scan
import utils4py.service

_logger = logging.getLogger(__name__)

_ATTR_FLASK_FLAG_IMPL = "_flask_flag_impl_"  # 标记是否是flask service实现
_ATTR_FLASK_ROUTE = "_flask_route_"  # path route
_ATTR_FLASK_ENABLE = "_flask_enable_"  # enable or not
_ATTR_FLASK_ENDPOINT = "_flask_endpoint_"  # route endpoint
_ATTR_FLASK_ALLOW_METHODS = "_flask_allow_methods_"  # allowed request methods, by default [GET,POST]
_ATTR_FLASK_TEMPLATE = "_flask_template_"  # template


class KvLogMixin(object):
    @classmethod
    def add_notice_log(cls, key, value):
        if not hasattr(flask.g, 'kv_log'):
            flask.g.kv_log = dict()
        flask.g.kv_log[key] = value
        return


@six.add_metaclass(abc.ABCMeta)
class BaseService(utils4py.service.BaseService, KvLogMixin):
    """
        Flask base service
    """

    RESP_KEY_TEMPLATE = "render_tpl"

    def _process_error(self, err):
        self.logger.error(traceback.format_exc())
        code = self.get_error_code(err)
        msg = self.get_error_message(err)  # type:str

        if not utils4py.env.is_debug:
            split_msg = msg.split('#', 1)
            if isinstance(split_msg, (list, tuple)):
                if len(split_msg) > 1:
                    self.add_notice_log('error_ext', split_msg[1])
                    return self.builder_cls.build(code, message=split_msg[0])

        return self.builder_cls.build(code, message=msg)


def service_route(**kwargs):
    """
    decorator for sub class of utils4py.flask_ext.routes.BaseService
    """
    _enable = kwargs.get("enable", True)
    _route = kwargs.get("route", "")
    _endpoint = kwargs.get("endpoint", "")
    _methods = kwargs.get("methods", None) or ['GET', 'POST']
    _template = kwargs.get("template", None)

    def _wrap_flask_service(cls):
        setattr(cls, _ATTR_FLASK_FLAG_IMPL, True)
        setattr(cls, _ATTR_FLASK_ENABLE, _enable)
        setattr(cls, _ATTR_FLASK_ROUTE, _route)
        setattr(cls, _ATTR_FLASK_ENDPOINT, _endpoint)
        setattr(cls, _ATTR_FLASK_ALLOW_METHODS, _methods)
        if _template:
            setattr(cls, _ATTR_FLASK_TEMPLATE, _template)
        return cls

    return _wrap_flask_service


def _service_factory(cls):
    """
    :param class cls:
    :return:
    """

    def _factory(*args, **kwargs):
        logger = getattr(flask.current_app, '_logger', _logger)
        try:
            obj = cls(logger=logger)  # type: BaseService
        except (Exception,):
            obj = cls()  # type: BaseService

        kwargs['logger'] = logger
        result = obj.execute(*args, **kwargs)
        builder_cls = getattr(obj, 'builder_cls', utils4py.service.ResultBuilder)

        try:
            code = result.get(builder_cls.key_error_code)
            flask.g.code = code
            if code != builder_cls.err_code_ok:
                msg = result.get(builder_cls.key_error_message)
                obj.add_notice_log("error", msg)
        except Exception as err:
            _logger.warning("path=%s, log code and error message fail, %s",
                            flask.request.path,
                            err)
            pass

        body = result.get(builder_cls.key_result_data)
        if isinstance(body, BaseResponse):
            return body

        # if template is given
        tpl = result.get(cls.RESP_KEY_TEMPLATE, None) or getattr(cls, _ATTR_FLASK_TEMPLATE, None)
        if tpl:
            return flask.render_template(tpl, **result)

        # finally return json
        return utils4py.TextUtils.json_dumps(result)

    return _factory


def _scan_implemented_services(path):
    """

    Find all usable sub class of `utils4py.flask_ext.route.BaseService` in package `path`

    :param str path:
    :return:
    """

    impl_cls = []

    for a_module in utils4py.scan.walk_modules(path):  # type: module

        for attr_name in vars(a_module):  # type: str

            # must not startswith '_' and its first letter should be upper case
            if attr_name.startswith('_') or not str.isupper(attr_name[0]):
                continue

            # exclude invalid attr
            attr_obj = getattr(a_module, attr_name)
            try:
                assert attr_obj, 'must not be empty'
                assert inspect.isclass(attr_obj), 'must be class'
                assert issubclass(attr_obj, BaseService), 'must be sub class of BaseService'
                assert attr_obj is not BaseService, 'must not be BaseService'
                assert attr_obj.__module__ == a_module.__name__, 'must be defined in this module'
            except AssertionError:
                continue

            # check class attribute, must be decorated by service_route
            try:
                assert getattr(attr_obj, _ATTR_FLASK_FLAG_IMPL, None) is True, 'must be decorated with service_route'
                assert getattr(attr_obj, _ATTR_FLASK_ENABLE, False) is True, 'must be enabled'
            except AssertionError:
                continue

            str_route = getattr(attr_obj, _ATTR_FLASK_ROUTE, "")
            default_endpoint = "{}.{}".format(a_module.__name__, attr_obj.__name__)

            if not str_route:
                str_route = default_endpoint.replace(path, "", 1).replace(".", "/")
                if not str_route.startswith("/"):
                    str_route = "/" + str_route
                setattr(attr_obj, _ATTR_FLASK_ROUTE, str_route)

            if not getattr(attr_obj, _ATTR_FLASK_ENDPOINT, ""):
                setattr(attr_obj, _ATTR_FLASK_ENDPOINT, default_endpoint)

            impl_cls.append(attr_obj)
            pass
        pass

    return impl_cls


def init_routes(app, paths):
    """
    Scan the given packages in paths, and auto bind route on app

    :param flask.Flask app: One instance of Flask app
    :param list[str] paths: A list packages wait to scan
    :return:
    """

    reg_center = dict()

    def _register_one_package(path):

        implemented_classes = _scan_implemented_services(path)
        if not implemented_classes:
            return

        for cls_obj in implemented_classes:
            if id(cls_obj) in reg_center:
                continue

            str_route = getattr(cls_obj, _ATTR_FLASK_ROUTE)
            str_endpoint = getattr(cls_obj, _ATTR_FLASK_ENDPOINT)
            methods = getattr(cls_obj, _ATTR_FLASK_ALLOW_METHODS)

            app.route(str_route, endpoint=str_endpoint, methods=methods)(_service_factory(cls_obj))

            _logger.info("----> [Register Service] route = %-35s , endpoint=%s ", str_route, str_endpoint)
            reg_center[id(cls_obj)] = cls_obj

            pass

        return

    for pkg in paths:
        _register_one_package(pkg)

    _logger.info("----> [Register Service] len = %s", len(reg_center))
    return


pass
