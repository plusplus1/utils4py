#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import Cursor, DictCursor
from pymysql.err import OperationalError

from utils4py import ConfUtils

_mysql_conf = ConfUtils.load_parser("mysql/default.conf")


def connect(section):
    params = _ConnectParams().init_with_section(section)
    return MySQLAgent(params)


class MySQLAgent(object):
    """
        MySQL Agent
    """

    def __init__(self, args):
        """
        :param _ConnectParams args: 
        """
        self._db_args = args
        self._db = None  # type:Connection
        self.reconnect()

    def __del__(self):
        self.close()

    def close(self):
        if self._db is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = self._db_args.connect()

    def _ensure_connected(self):
        if self._db is None:
            self.reconnect()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, *args, **kwargs):
        """
        :param Cursor cursor: 
        :param str query: 
        :return: 
        """
        try:
            return cursor.execute(query, kwargs or args)
        except OperationalError:
            logging.error("Error connecting to MySQL on %s", self._db_args.host)
            self.close()
            raise

    def query(self, query, *args, **kwargs):
        cursor = self._cursor()
        try:
            self._execute(cursor, query, *args, **kwargs)
            return [row for row in cursor]
        finally:
            cursor.close()

    def get(self, query, *parameters, **kwparameters):
        """Returns the (singular) row returned by the given query.

        If the query has no results, returns None.  If it has
        more than one result, raises an exception.
        """
        rows = self.query(query, *parameters, **kwparameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    # rowcount is a more reasonable default return value than lastrowid,
    # but for historical compatibility execute() must return lastrowid.
    def execute(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        return self.execute_lastrowid(query, *parameters, **kwparameters)

    def execute_lastrowid(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, *parameters, **kwparameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the rowcount from the query."""
        cursor = self._cursor()
        try:
            self._execute(cursor, query, *parameters, **kwparameters)
            return cursor.rowcount
        finally:
            cursor.close()

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            return cursor.rowcount
        finally:
            cursor.close()

    update = execute_rowcount
    updatemany = executemany_rowcount

    insert = execute_lastrowid
    insertmany = executemany_lastrowid

    pass


class _ConnectParams(object):
    """
        mysql 连接参数
    """

    def __init__(self):
        self._host = "localhost"
        self._port = 3306
        self._user = ""
        self._password = ""
        self._db = ""
        self._time_zone = "+8:00"
        self._charset = 'utf8'
        pass

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port or 3306

    @property
    def password(self):
        return self._password or ""

    @property
    def user(self):
        return self._user

    @property
    def db(self):
        return self._db

    @property
    def charset(self):
        return self._charset or 'utf8'

    @property
    def time_zone(self):
        return self._time_zone or '+8:00'

    def init_with_section(self, section_name):
        items = dict(_mysql_conf.items(section_name))
        self._host = str.strip(items.get('host', ""))
        self._port = int(items.get('port', 3306))
        self._user = str.strip(items.get('user', ""))
        self._password = str.strip(items.get('password', ""))
        self._db = str.strip(items.get('db', ""))
        self._time_zone = str.strip(items.get('time_zone', '+8:00'))
        self._charset = str.strip(items.get('charset', 'utf8'))
        return self

    def connect(self):
        """
        :return: 
        :rtype: Connection
        """

        time_zone = self.time_zone
        init_command = None
        if time_zone:
            init_command = 'SET time_zone = "%s"' % time_zone

        conn = pymysql.connect(host=self.host,
                               port=self.port,
                               database=self.db,
                               user=self.user,
                               password=self.password,
                               use_unicode=True,
                               autocommit=True,
                               init_command=init_command,
                               charset=self.charset,
                               sql_mode="TRADITIONAL",
                               cursorclass=DictCursor,
                               )

        return conn

    def __str__(self):
        return json.dumps({'host'     : self.host,
                           'port'     : self.port,
                           'database' : self.db,
                           'user'     : self.user,
                           'password' : self.password,
                           'time_zone': self.time_zone,
                           'charset'  : self.charset,
                           })

    pass
