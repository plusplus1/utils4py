#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from utils4py.conf import ConfUtils
from utils4py.env import env
from utils4py.errors import SimpleError
from utils4py.errors import overwrite_error_codes
from utils4py.text import TextUtils

__version__ = '0.1.18'

_logger = logging.getLogger(__name__)


def adapt(**kwargs):
    from utils4py.service import ResultBuilder
    from utils4py.errors import ErrorMixin

    if 'key_error_code' in kwargs:
        ResultBuilder.key_error_code = kwargs['key_error_code']
    if 'key_error_message' in kwargs:
        ResultBuilder.key_error_message = kwargs['key_error_message']
    if 'key_result_data' in kwargs:
        ResultBuilder.key_result_data = kwargs['key_result_data']
    if 'err_code_ok' in kwargs:
        ResultBuilder.err_code_ok = kwargs['err_code_ok']
    if 'err_code_parameter' in kwargs:
        ErrorMixin.err_code_parameter = kwargs['err_code_parameter']
    if 'err_code_unknown' in kwargs:
        ErrorMixin.err_code_unknown = kwargs['err_code_unknown']
    return


__all__ = [
    'env',
    'overwrite_error_codes',
    'SimpleError',
    'TextUtils',
    'ConfUtils',
    'adapt',
]
