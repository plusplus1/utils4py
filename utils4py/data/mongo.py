#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

from pymongo import MongoClient
from pymongo.database import Database
from six.moves.urllib.parse import quote_plus

from utils4py import ConfUtils

settings_reuse_pool = True

_mongo_conf = ConfUtils.load_parser("data_source/mongo.conf")

_conn_pool = dict()
_reuse_mutex = threading.RLock()


def _connect(section):
    params = _ConnectParams().init_with_section(section)
    params.connect()
    return params


def connect(section):
    """
    :param section: 
    :rtype: Database
    """

    if settings_reuse_pool:
        try:
            _reuse_mutex.acquire()
            if section not in _conn_pool:
                _conn_pool[section] = _connect(section)
            params = _conn_pool[section]
            return params.client.get_database(params.db_name)
        finally:
            _reuse_mutex.release()
    else:
        params = _connect(section)
        return params.client.get_database(params.db_name)


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

        self._client = ""
        pass

    @property
    def client(self):
        """
        :rtype: MongoClient 
        """
        return self._client

    @property
    def db_name(self):
        return self._db

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
        self._client = MongoClient(uri)
        return self._client

    # def __del__(self):
    #     if self.client:
    #         self.client.close()
    #         self._client = None
    pass


pass
