#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import threading

import redis
import redis.client

from utils4py import ConfUtils, TextUtils

_redis_conf = ConfUtils.load_parser("data_source/redis.conf")

settings_reuse_pool = True
_conn_pool = dict()
_reuse_mutex = threading.RLock()


def connect(section):
    if settings_reuse_pool:
        with _reuse_mutex:
            conn = _conn_pool.get(section, None)
            if not conn:
                conn = _ConnectParams().init_with_section(section).connect()
                if conn:
                    _conn_pool[section] = conn
            return conn
    else:
        params = _ConnectParams().init_with_section(section)
        return params.connect()


class _RedisWrapper(object):
    """
        Redis
    """

    _method_groups_1 = {'hexists', 'decr', 'exists', 'expire', 'get',
                        'getset', 'hdel', 'hget', 'hgetall', 'hkeys',
                        'hlen', 'hmget', 'hmset', 'hset', 'hsetnx',
                        'incr', 'keys', 'llen', 'lpop', 'lpush', 'lrange', 'lindex',
                        'rpop', 'rpush', 'sadd', 'set', 'setex', 'setnx',
                        'sismember', 'smembers', 'srem', 'ttl', 'type', }

    _method_groups_2 = {"delete", "mget"}

    def __init__(self, client, key_prefix):
        self._client = client  # type:redis.Redis
        self._key_prefix = key_prefix  # type:str

    def __getattr__(self, item):
        try:
            assert item in self._method_groups_1 or item in self._method_groups_2
            method = getattr(self._client, item)
            assert method
        except:
            raise AttributeError(item)

        if item in self._method_groups_1:
            def _inner(*args, **kwargs):
                arg_lst = list(args)
                a0 = self.make_key(arg_lst[0])
                arg_lst[0] = a0
                return method(*tuple(arg_lst), **kwargs)
        else:
            def _inner(*args, **kwargs):
                arg_lst = list(args)
                a0 = arg_lst[0]
                a_els = arg_lst[1:]
                a_new = list(map(
                    self.make_key,
                    redis.client.list_or_args(a0, a_els)
                ))
                return method(*tuple(a_new), **kwargs)

        return _inner

    def ping(self):
        return self._client.ping()

    def make_key(self, key):
        return "{}:{}".format(self._key_prefix, key)


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
