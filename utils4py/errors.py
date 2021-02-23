#!/usr/bin/env python
# -*- coding: utf-8 -*-


import six

from utils4py.text import TextUtils

_error_map = {
    "100": "ParameterError",
    "500": "ServiceInternalError",
    "1000": "UnknownError"
}


def overwrite_error_codes(code_map):
    """
    when write business code, overwrite default error code map first
    :param code_map:
    :return:
    """
    for k, v in six.iteritems(code_map):
        _error_map[TextUtils.to_string(k)] = v


class SimpleError(Exception):
    """ Simple Error """

    def __init__(self, code, message=None):
        msg = "#".join(filter(lambda x: x, [_error_map.get(TextUtils.to_string(code), ''),
                                            '' if message is None else TextUtils.to_string(message)]))
        Exception.__init__(self, *(code, msg))

    @property
    def code(self):
        return self.args[0]

    @property
    def message(self):
        return self.args[1]

    def __str__(self):
        return "|".join(filter(lambda x: x, map(TextUtils.to_string, self.args)))

    pass


class ErrorMixin(object):
    """
        Error Utilities
    """

    err_code_parameter = 100  # parameter error
    err_code_unknown = 1000  # unknown error

    @classmethod
    def build_error(cls, code, message=None):
        return SimpleError(code, message)

    @classmethod
    def get_error_code(cls, err):
        """
        :param Exception err:
        :return:
        """
        code = None
        if isinstance(err, SimpleError):
            code = err.code
        elif err.args and isinstance(err.args, (tuple, list)) and len(err.args) > 0:
            code = err.args[0]

        if isinstance(code, six.integer_types):
            return code
        try:
            return int(code)
        except (Exception,):
            return cls.err_code_unknown

    @classmethod
    def get_error_message(cls, err):
        """
        :param Exception err:
        :return:
        """

        if isinstance(err, SimpleError):
            return TextUtils.to_string(err.message)

        if err.args and isinstance(err.args, (tuple, list)) and len(err.args) > 1:
            return TextUtils.to_string(err.args[1])

        return str(err)

    @classmethod
    def build_parameter_error(cls, message=None):
        return SimpleError(cls.err_code_parameter, message)

    pass


pass
