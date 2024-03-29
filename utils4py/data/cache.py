#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import threading

import redis
import redis.client
import rediscluster
import six
from werkzeug.utils import cached_property

from utils4py import ConfUtils, TextUtils

try:
    _redis_conf = ConfUtils.load_yaml("data_source/redis.yaml")
except (Exception,):
    _redis_conf = dict()

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

    @cached_property
    def raw_client(self):
        """
        :rtype: redis.Redis
        """
        return self._client

    def __getattr__(self, item):
        try:
            assert item in self._method_groups_1 or item in self._method_groups_2
            method = getattr(self._client, item)
            assert method
        except BaseException:
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

    def pipeline(self, *args, **kwargs):
        return self._client.pipeline(*args, **kwargs)


class _ConnectParams(object):
    """
        redis
    """

    _default_params = {
        'host': "localhost",
        "port": 6379,
        "password": "",
        "db": 0,
    }

    _default_connect_timeout_ms = 1000.0
    _default_read_timeout_ms = 500.0

    """
    # 集群模式：参数
    args = dict(startup_nodes=[dict(zip(['host', 'port'], b)) for b in nodes], password=redis_config.get('password', ''),
                    socket_connect_timeout=connect_ms / 1000., socket_timeout=read_ms / 1000.,
                    skip_full_coverage_check=True, )
    """

    def __init__(self):
        self._params = dict()
        self._section = None

    def init_with_section(self, section_name):
        self._section = section_name
        self._params.setdefault("socket_connect_timeout", self._default_connect_timeout_ms)
        self._params.setdefault("socket_timeout", self._default_read_timeout_ms)

        _raw_cfg = _redis_conf[section_name]  # type: dict
        _is_cluster_mode = _raw_cfg.get('startup_nodes')

        if _is_cluster_mode:
            self._params.setdefault("skip_full_coverage_check", True)
        else:
            self._params.update(self._default_params)

        for k, v in six.iteritems(_raw_cfg):
            self._params[k] = v

        if not _is_cluster_mode:
            self._params['port'] = int(self._params['port'])
            self._params['db'] = int(self._params['db'])
        else:
            startup_nodes = self._params['startup_nodes']
            if startup_nodes and isinstance(startup_nodes, list) and isinstance(startup_nodes[0], str):
                startup_nodes = list(map(lambda y: dict(zip(['host', 'port'], (y[0], int(y[1])))), [x.split(':', 1) for x in startup_nodes]))
            for node in startup_nodes:
                node['port'] = int(node['port'])
            self._params['startup_nodes'] = startup_nodes

        # timeout 配置默认都是毫秒
        for _timeout_ms in ['socket_connect_timeout', 'socket_timeout']:
            if _timeout_ms in self._params:
                self._params[_timeout_ms] = float(self._params[_timeout_ms]) / 1000.

        return self

    def connect(self):
        """
        :return:
        :rtype: redis.Redis
        """
        clz = rediscluster.RedisCluster if self._params.get("startup_nodes", None) else redis.Redis
        conn = clz(**self._params)
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
