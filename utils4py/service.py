#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import logging
import traceback

from six import add_metaclass, iteritems

from utils4py import env
from utils4py.errors import ErrorMixin
from utils4py.errors import SimpleError

_logger = logging.getLogger(__name__)


class ResultBuilder(object):
    """
        Result builder
    """

    err_code_ok = 0

    key_error_code = "errno"
    key_error_message = "msg"
    key_result_data = "data"

    @classmethod
    def build(cls, code, message=None, data=None, appends=None):
        ret = {cls.key_error_code: code, cls.key_error_message: message or ""}
        if data is not None:
            ret[cls.key_result_data] = data

        if appends and isinstance(appends, dict):
            for k, v in iteritems(appends):
                if k == cls.key_result_data or k == cls.key_error_code or k == cls.key_error_message:
                    continue
                ret[k] = v

        return ret


@add_metaclass(abc.ABCMeta)
class BaseService(ErrorMixin):
    """

      Base service for write business code, for convenience, you do not care about error handle ,

      all things you should do as follow:

        - If your business need validate input parameters, overwrite check_args method and raise
          any error when some parameter is invalid.

        - Overwrite run method, implement business logic.

        - If you want for trans format result from `run` method, overwrite format_result method,
          and return a new formatted result.

    """

    builder_cls = ResultBuilder

    def __init__(self, **kwargs):
        self._logger = kwargs.get('logger') or _logger
        pass

    @property
    def logger(self):
        return getattr(self, '_logger', _logger)

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        """
        Implement this method in sub class, and rite you business logic.
        """
        raise NotImplemented

    def check_args(self, *args, **kwargs):
        """
        If it's necessary validate input parameters, overwrite this method.
        If some parameter is invalid, just raise any error
        """
        id(self)
        pass

    def format_result(self, result):
        """
        If it's necessary to trans format result from `run` method,
        overwrite this method
        """
        id(self)
        return result

    def init(self, *args, **kwargs):
        """
        Normally , call check_args here, and capture check args exception

        :param args:
        :param kwargs:
        :return:
        """
        if 'logger' in kwargs:
            self._logger = kwargs.get('logger', _logger)

        try:
            self.check_args(*args, **kwargs)
        except Exception as err:
            if isinstance(err, SimpleError):
                raise err

            raise self.build_parameter_error(str(err))  # by default, build simple error

    def _process_error(self, err):
        self.logger.error(traceback.format_exc())
        code = self.get_error_code(err)
        msg = self.get_error_message(err)
        return ResultBuilder.build(code, message=msg)

    def execute(self, *args, **kwargs):
        """
        service entry point
        """

        try:
            self.init(*args, **kwargs)  # do init first, by default check args
            result, appends = None, None

            for _ in [0]:
                if env.is_debug:  # when debug mode, run
                    run_method = getattr(self, 'mock_run', None)
                    if run_method and callable(run_method):
                        ret_run = run_method(*args, **kwargs)
                        if ret_run:
                            break
                ret_run = self.run(*args, **kwargs)
                break

            if ret_run and isinstance(ret_run, tuple):
                result = ret_run[0] if len(ret_run) > 0 else None
                appends = ret_run[1] if len(ret_run) > 1 else None
            else:
                result = ret_run

            result = self.format_result(result)
            return ResultBuilder.build(ResultBuilder.err_code_ok, data=result, appends=appends, )
        except Exception as err:
            return self._process_error(err)

        pass

    pass
