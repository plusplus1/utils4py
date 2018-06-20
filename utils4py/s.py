#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json

import six


class TextUtils(object):
    """
        Text utilities
    """

    class _JSONEncoder(json.JSONEncoder):
        """
            default json encoder handle datetime
        """

        def default(self, o):  # pylint: disable=E0202
            if isinstance(o, datetime.datetime):
                return o.strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(o, datetime.date):
                return o.strftime('%Y-%m-%d')
            return json.JSONEncoder.default(self, o)

        pass

    @classmethod
    def to_string(cls, value):
        if isinstance(value, six.text_type):
            return value.encode('utf8')
        if isinstance(value, six.string_types):
            return value
        if isinstance(value, Exception):
            return cls.to_string(value.message)
        if value is None:
            return ""
        return str(value)

    @classmethod
    def json_dumps(cls, val, indent=None, encoder_cls=None):
        e_cls = encoder_cls if encoder_cls else cls._JSONEncoder
        if isinstance(indent, six.integer_types):
            return json.dumps(val, indent=indent, cls=e_cls)
        return json.dumps(val, cls=e_cls)

    @classmethod
    def json_loads(cls, val):
        if isinstance(val, six.string_types):
            return json.loads(val)
        return json.load(val)

    pass


pass
