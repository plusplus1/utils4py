#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json

import redis
import redis.client

from utils4py import ConfUtils, TextUtils

_redis_conf = ConfUtils.load_parser("redis/default.conf")


def connect(section):
    params = _ConnectParams().init_with_section(section)
    return params.connect()


class _RedisWrapper(object):
    """
        Redis
    """

    _method_groups_1 = ['hexists', 'decr', 'exists', 'expire', 'get',
                        'getset', 'hdel', 'hget', 'hgetall', 'hkeys',
                        'hlen', 'hmget', 'hmset', 'hset', 'hsetnx',
                        'incr', 'keys', 'llen', 'lpop', 'lpush', 'lrange', 'lindex',
                        'rpop', 'rpush', 'sadd', 'set', 'setex', 'setnx',
                        'sismember', 'smembers', 'srem', 'ttl', 'type', ]

    _method_groups_2 = ["delete", "mget"]

    def __init__(self, client, key_prefix):
        self._client = client  # type:redis.Redis
        self._key_prefix = key_prefix  # type:str

        for m in self._method_groups_1:
            wm = self._wrapper_str_args(getattr(self._client, m))
            setattr(self, m, wm)

        for m in self._method_groups_2:
            wm = self._wrapper_tuple_args(getattr(self._client, m))
            setattr(self, m, wm)

        pass

    def ping(self):
        return self._client.ping()

    def make_key(self, key):
        return "{}:{}".format(self._key_prefix, key)

    def _wrapper_str_args(self, func):
        """

        :param func: 
        :return: 
        """

        def _inner(*args, **kwargs):
            arg_list = list(args)
            arg_list[0] = self.make_key(arg_list[0])
            return func(*tuple(arg_list), **kwargs)

        return _inner

    def _wrapper_tuple_args(self, func):
        """

        :param func: 
        :return: 
        """

        def _inner(*args, **kwargs):
            arg_list = list(args)
            arg0 = arg_list[0]
            arg_else = arg_list[1:]

            new_args = map(
                lambda x: self.make_key(x),
                redis.client.list_or_args(arg0, arg_else)
            )

            return func(*tuple(new_args), **kwargs)

        return _inner

    pass


class _ConnectParams(object):
    """
        redis
    """

    _default_params = {
        'host'    : "localhost",
        "port"    : 6379,
        "password": "",
        "db"      : 0,
    }

    def __init__(self):
        self._params = copy.deepcopy(_ConnectParams._default_params)
        self._section = None

    def init_with_section(self, section_name):
        self._section = section_name
        for k, v in _redis_conf.items(section_name):
            self._params[k] = v
        self._params['port'] = int(self._params['port'])
        self._params['db'] = int(self._params['db'])
        return self

    def connect(self):
        """
        :return: 
        :rtype: redis.Redis
        """

        conn = redis.Redis(**self._params)
        if conn.ping():
            return _RedisWrapper(conn, self._section)

        return None

    def __str__(self):
        return json.dumps(self._params)


class SimpleQueue(object):
    """
        Redis simple queue
    """

    def __init__(self, queue_name, section=None, client=None):
        self._queue_name = queue_name
        assert section or client

        self._client_section = section
        self._client = client

    @property
    def client(self):
        if not self._client:
            self._client = connect(self._client_section)
        return self._client

    def push(self, data):
        s = TextUtils.json_dumps(data) if isinstance(data, (list, dict)) else TextUtils.to_string(data)
        return self.client.lpush(self._queue_name, s)

    def pop(self):
        return self.client.rpop(self._queue_name)

    def size(self):
        return self.client.llen(self._queue_name)

    pass


pass
