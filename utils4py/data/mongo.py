#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from six.moves.urllib.parse import quote_plus

from utils4py import ConfUtils

_mongo_conf = ConfUtils.load_parser("data_source/mongo.conf")


def connect(section):
    params = _ConnectParams().init_with_section(section)
    return params.connect()


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
