#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import decimal
import hashlib
import json

import six


class JSONEncoder(json.JSONEncoder):
    """
        default json encoder handle datetime
    """

    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return datetime.date.strftime(o, '%Y-%m-%d')
        else:
            return super(JSONEncoder, self).default(o)

    pass


class TextUtils(object):
    """
        Text utilities
    """

    default_json_encoder = JSONEncoder
    default_separators = (',', ':')

    @classmethod
    def json_dumps(cls, val, **kwargs):
        kw = {
            'cls'         : kwargs.get('encoder_cls', cls.default_json_encoder),
            'separators'  : kwargs.get('separators', cls.default_separators),
            'indent'      : kwargs.get('indent', None),
            'ensure_ascii': kwargs.get('ensure_ascii', None),
            'sort_keys'   : kwargs.get('sort_keys', None),
        }
        return json.dumps(val, **kw)

    @classmethod
    def json_loads(cls, val):
        if six.PY3:
            if isinstance(val, (str, bytes)):
                return json.loads(val)
        else:
            if isinstance(val, six.string_types):
                return json.loads(val)
        return json.load(val)

    @classmethod
    def md5_string(cls, val):
        if isinstance(val, six.text_type):
            return hashlib.md5(val.encode('utf8')).hexdigest()
        return hashlib.md5(val).hexdigest()

    @classmethod
    def to_string(cls, val):
        if six.PY3:
            if isinstance(val, six.text_type):
                return val
        else:
            if isinstance(val, six.text_type):
                return val.encode('utf8')
            if isinstance(val, str):
                return val
        return str(val)

    pass


pass
