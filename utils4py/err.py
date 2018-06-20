#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from s import TextUtils


class ErrUtils(object):
    """
        Error Utilities
    """

    err_code_parameter = 100  # parameter error
    err_code_unknown = -1000  # unknown error

    @classmethod
    def build_error(cls, code, message):
        return Exception(code, message)

    @classmethod
    def get_code(cls, err):
        """
        
        :param Exception err: 
        :return: 
        """
        if err.args and isinstance(err.args, (tuple, list)) and len(err.args) > 0:
            code = err.args[0]
            if isinstance(code, six.integer_types):
                return code

        return cls.err_code_unknown

    @classmethod
    def get_message(cls, err):
        """
        :param Exception err: 
        :return: 
        """
        if err.args and isinstance(err.args, (tuple, list)) and len(err.args) > 1:
            return TextUtils.to_string(err.args[1])
        return TextUtils.to_string(err.message)

    @classmethod
    def build_parameter_error(cls, message=None):
        return cls.build_error(cls.err_code_parameter, message or 'parameter error')

    pass
