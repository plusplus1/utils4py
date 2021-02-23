#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import logging
import os
import time

import pymysql.err
from pymysql.cursors import DictCursor

from utils4py.pymysql_pool.pool import Connection, Pool

_logger = logging.getLogger(__name__)

try:
    _echo = str.upper(os.environ.get("utils4py.pymysql_pool.echo", ""))
    if _echo and _echo in {'1', 'T', 'TRUE'}:
        _echo_sql_statement = True
    else:
        _echo_sql_statement = False
except (Exception,):
    _echo_sql_statement = False

LOG_SQL_STATEMENT = _echo_sql_statement  # 兼容


class MultipleRowsError(pymysql.err.DataError):
    pass


class BaseShell(object):
    """Shell mixin"""

    __metaclass__ = abc.ABCMeta

    REUSABLE_EXCEPTIONS = (pymysql.err.ProgrammingError,
                           pymysql.err.NotSupportedError,
                           pymysql.err.IntegrityError,
                           MultipleRowsError,)

    MYSQL_EXCEPTIONS = (pymysql.err.MySQLError,)

    @abc.abstractmethod
    def cursor(self):
        pass

    @abc.abstractmethod
    def _reset(self, reusable=None):
        pass

    @classmethod
    def is_reusable_error(cls, exc_val):
        if exc_val and isinstance(exc_val, cls.MYSQL_EXCEPTIONS) \
                and not type(exc_val) in cls.REUSABLE_EXCEPTIONS:
            return False
        return True

    def _execute(self, cursor, query, *args, **kwargs):
        """
        :param DictCursor cursor:
        :param query:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            if _echo_sql_statement:
                _logger.info("\t[Sql Statement] sql = %s, args = %s", query, kwargs or args)

            if len(kwargs or args) > 0:
                return cursor.execute(query, kwargs or args)
            else:
                return cursor.execute(query)
        except Exception as err:
            self._reset(self.is_reusable_error(err))
            raise

    def _execute_many(self, cursor, query, args):
        """
        :param DictCursor cursor:
        :param query:
        :param args:
        :return:
        """
        try:
            if _echo_sql_statement:
                _logger.info("\t[Sql Statement] sql = %s, args = %s", query, args)

            return cursor.executemany(query, args)
        except Exception as err:
            self._reset(self.is_reusable_error(err))
            raise

    def query(self, query, *args, **kwargs):
        with self.cursor() as cursor:
            self._execute(cursor, query, *args, **kwargs)
            return [row for row in cursor]

    def get(self, query, *parameters, **kwargs):
        rows = self.query(query, *parameters, **kwargs)
        if not rows:
            return None
        elif len(rows) > 1:
            raise MultipleRowsError("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def execute_lastrowid(self, query, *args, **kwargs):
        with self.cursor() as cursor:
            self._execute(cursor, query, *args, **kwargs)
            return cursor.lastrowid

    def execute_rowcount(self, query, *args, **kwargs):
        with self.cursor() as cursor:
            self._execute(cursor, query, *args, **kwargs)
            return cursor.rowcount

    def executemany_lastrowid(self, query, args):
        with self.cursor() as cursor:
            self._execute_many(cursor, query, args)
            return cursor.lastrowid

    def executemany_rowcount(self, query, args):
        with self.cursor() as cursor:
            self._execute_many(cursor, query, args)
            return cursor.rowcount

    execute = execute_rowcount
    executemany = executemany_rowcount

    update = execute_rowcount
    updatemany = executemany_rowcount

    insert = execute_lastrowid
    insertmany = executemany_lastrowid

    pass


class SqlShell(BaseShell):
    """ sql shell """

    _TAG = "\t[SqlShell]"

    def __init__(self, pool):
        self._pool = pool  # type: Pool
        self._connection = None  # type:Connection

    def _reset(self, reusable=None):
        if not self._connection:
            return

        _logger.debug("%s %s reset, conn = %s, reusable = %s", self._TAG, id(self), id(self._connection), reusable)

        if self._pool:
            can_reuse = False if reusable is False else True
            self._pool.release(self._connection, can_reuse=can_reuse)

        self._connection = None
        return

    def __enter__(self):
        _logger.debug("%s %s enter sql shell", self._TAG, id(self))
        self._reset(None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._reset(self.is_reusable_error(exc_val))
        _logger.debug("%s %s exit Sql Shell", self._TAG, id(self))
        pass

    def cursor(self):
        """
        :rtype: DictCursor
        """
        if not self._connection:
            self._connection = self._pool.get_connection()

        if time.time() - self._connection.last_use_time > self._connection.max_idle_time:
            self._connection.ping(reconnect=True)

        c = self._connection.cursor()
        self._connection.last_use_time = time.time()
        return c

    def begin_trans(self):
        return _TransactionSqlShell(self._pool)

    pass


class _TransactionSqlShell(BaseShell):
    """trans shell"""

    _TAG = '\t[TransactionSqlShell]'

    def __init__(self, pool):
        self._pool = pool  # type:Pool
        self._connection = self._pool.get_connection()
        self._committed = False  # by default, transaction is not committed
        self._can_reuse = True  # by default, connection can be reused
        self._started = False
        pass

    def _reset(self, reusable=None):
        if not self._can_reuse:  # if connection is already unusable, return directly
            return
        if reusable is False:
            self._can_reuse = False
        return

    def cursor(self):
        c = self._connection.cursor()
        self._connection.last_use_time = time.time()
        return c

    def _execute(self, cursor, query, *args, **kwargs):
        if not self._started:
            raise Exception('transaction is not begin')

        return super(_TransactionSqlShell, self)._execute(cursor, query, *args, **kwargs)

    def _execute_many(self, cursor, query, args):
        if not self._started:
            raise Exception('transaction is not begin')

        return super(_TransactionSqlShell, self)._execute_many(cursor, query, args)

    def __enter__(self):  # start transaction
        if self._started:
            raise Exception('you should not start transaction repeated')

        self._connection.begin()
        self._started = True

        _logger.debug('%s %s start transaction ok', self._TAG, id(self))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # commit transaction and release connection
        try:
            if exc_val:
                self._connection.rollback()
                _logger.debug('%s %s end transaction with rollback.', self._TAG, id(self))
            else:
                self._connection.commit()
                _logger.debug('%s %s end transaction with commit.', self._TAG, id(self))
        except Exception as err:
            _logger.error("%s %s end transaction fail, error=%s", self._TAG, id(self), err)
            self._reset(False)

        self._reset(self.is_reusable_error(exc_val))

        try:
            self._pool.release(self._connection, self._can_reuse)
        finally:
            self._connection = None
            self._pool = None
            self._committed = True
        return
