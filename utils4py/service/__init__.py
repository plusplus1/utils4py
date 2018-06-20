#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2018 yongqianbao.com, Inc. All Rights Reserved
#
########################################################################

"""
File: __init__.py.py
Author: chengyunlai(chengyunlai@daixiaomi.com)
Date: 2018/06/20 11:30:44
"""

import abc
import logging
import traceback

from six import iteritems

import utils4py
from utils4py.mixin import ArgMixin, ErrMixin


class ResultBuilder(object):
    """
        Result builder
    """

    ERROR_CODE_OK = 0

    KEY_ERROR_CODE = "errno"
    KEY_ERROR_MESSAGE = "msg"
    KEY_RESULT_DATA = "data"

    @classmethod
    def build(cls, code, message=None, data=None, appends=None):
        ret = {cls.KEY_ERROR_CODE: code, cls.KEY_ERROR_MESSAGE: message or ""}
        if data:
            ret[cls.KEY_RESULT_DATA] = data

        if appends and isinstance(appends, dict):
            for k, v in iteritems(appends):
                if k == cls.KEY_RESULT_DATA or k == cls.KEY_ERROR_CODE or k == cls.KEY_ERROR_MESSAGE:
                    continue
                ret[k] = v

        return ret


class BaseService(ErrMixin, ArgMixin):
    """
        base service 
    """

    __metaclass__ = abc.ABCMeta

    error_code_parameter = 100

    def __init__(self, **kwargs):
        self._logger = kwargs.get('logger') or logging
        pass

    @property
    def logger(self):
        return self._logger

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def check_args(self, *args, **kwargs):
        pass

    def mock_run(self, *args, **kwargs):
        id(self)
        return 0

    @classmethod
    def format_result(cls, result):
        return result

    def init(self, *args, **kwargs):
        self.check_args(*args, **kwargs)

    def execute(self, *args, **kwargs):

        try:
            self.init(*args, **kwargs)
            result, appends = None, None

            if utils4py.env.is_debug():
                r = self.mock_run(*args, **kwargs)  # pylint: disable=E1111
                if not r:
                    r = self.run(*args, **kwargs)
            else:
                r = self.run(*args, **kwargs)

            if r and isinstance(r, tuple):
                result = r[0] if len(r) > 0 else None
                appends = r[1] if len(r) > 1 else None
            else:
                result = r

            if result:
                result = self.format_result(result)

            return ResultBuilder.build(ResultBuilder.ERROR_CODE_OK, data=result, appends=appends)

        except Exception as err:
            self.logger.error(traceback.format_exc())
            code = self.get_code(err)
            msg = self.get_message(err)
            return ResultBuilder.build(code, message=msg)

        pass

    pass


pass
