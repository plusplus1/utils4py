#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

import pymongo
from six.moves.urllib.parse import quote_plus

from utils4py import ConfUtils

settings_reuse_pool = True

_mongo_conf = ConfUtils.load_parser("data_source/mongo.conf")

_conn_pool = dict()
_reuse_mutex = threading.RLock()


def _connect(section):
    params = _ConnectParams().init_with_section(section)
    return params.connect()


def connect(section):
    """
    :param section: 
    :rtype: pymongo.MongoClient
    """
    if settings_reuse_pool:
        try:
            _reuse_mutex.acquire()
            if section in _conn_pool:
                return _conn_pool[section]

            conn = _connect(section)
            _conn_pool[section] = conn
            return conn
        finally:
            _reuse_mutex.release()
    else:
        return _connect(section)


class _ConnectParams(object):
    """
        mongo connect params
    """

    def __init__(self):
        self._user = ""
        self._password = ""
        self._host = ""
        self._db = ""
        self._params = ""
        pass

    def init_with_section(self, section):
        conf = dict(_mongo_conf.items(section=section))
        self._user = conf.get("user", "")
        self._password = conf.get("password", "")
        self._host = conf.get("host", "")
        self._db = conf.get("db", "")
        self._params = conf.get("params", "")
        return self

    def connect(self):
        if self._user and self._password:
            uri = "mongodb://%s:%s@%s" % (quote_plus(self._user), quote_plus(self._password), self._host)
        else:
            uri = "mongodb://%s" % self._host
        uri = "%s/%s" % (uri, self._db)
        if self._params:
            uri = uri + "?" + self._params
        # print uri
        mgo = pymongo.MongoClient(uri)
        return mgo.get_database(self._db)

    pass


pass
