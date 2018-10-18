#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import pymysql.err
from pymysql.cursors import DictCursor

from utils4py.pymysql_pool.log import *
from utils4py.pymysql_pool.pool import Connection, Pool


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
            return cursor.execute(query, kwargs or args)
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

    def __init__(self, pool):
        self._pool = pool  # type: Pool
        self._connection = None  # type:Connection

    def _reset(self, reusable=None):
        if not self._connection:
            return
        log_debug("_result in shell, conn = %s, reusable = %s", self._connection, reusable)
        if self._pool:
            can_reuse = False if reusable is False else True
            self._pool.release(self._connection, can_reuse=can_reuse)

        self._connection = None
        return

    def __enter__(self):
        log_debug("+++ enter Sql Shell")
        self._reset(None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._reset(self.is_reusable_error(exc_val))
        log_debug("+++ exit Sql Shell")
        pass

    def __del__(self):
        self._reset(None)
        self._pool = None

    def cursor(self):
        """
        :rtype: DictCursor
        """
        if not self._connection:
            self._connection = self._pool.get_connection()
        return self._connection.cursor()

    def begin_trans(self):
        return _TransactionSqlShell(self._pool)

    pass


class _TransactionSqlShell(BaseShell):
    """trans shell"""

    def __init__(self, pool):
        self._pool = pool  # type:Pool
        self._connection = self._pool.get_connection()
        self._original_autocommit = self._connection.get_autocommit()
        self._connection.autocommit(False)

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
        return self._connection.cursor()

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

        log_debug("=== start transaction ok")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # commit transaction and release connection
        try:
            if exc_val:
                self._connection.rollback()
            else:
                self._connection.commit()

            if self._original_autocommit is not None:
                self._connection.autocommit(self._original_autocommit)

            log_debug(" === end transaction ok")
        except Exception as err:
            self._reset(self.is_reusable_error(err))
            log_debug(" === end transaction failed")

        self._reset(self.is_reusable_error(exc_val))

        try:
            self._pool.release(self._connection, self._can_reuse)
        finally:
            self._connection = None
            self._pool = None
            self._committed = True
        return

    def __del__(self):
        try:
            if self._pool and self._connection:
                if self._original_autocommit is not None:
                    self._connection.autocommit(self._original_autocommit)
                self._pool.release(self._connection, self._can_reuse)
        except (Exception,):
            pass

        self._pool = None
        self._connection = None
        return


pass
