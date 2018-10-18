#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
from itertools import chain

import pymysql
import pymysql.connections

from utils4py.pymysql_pool.log import *


class Connection(pymysql.connections.Connection):
    """Connection"""

    def __init__(self, **kwargs):
        pymysql.connections.Connection.__init__(self, **kwargs)
        self.pid = 0

    def __del__(self):
        try:
            self._force_close()
        except Exception as err:
            log_error("close connection error, %s, %s", self, err)

    pass


class Pool(object):
    """ pool """

    def __init__(self, **connect_args):
        self.connection_args = connect_args

        self.pid = 0
        self._check_lock = None
        self._created_connections = None  # type:int
        self._available_connections = None  # type:list
        self._created_count_lock = None
        self.reset()

    def reset(self):
        self.pid = os.getpid()
        self._check_lock = threading.Lock()
        self._created_count_lock = threading.Lock()
        self._created_connections = 0
        self._available_connections = list()
        return

    def _atom_increment_created_count(self, cnt):
        with self._created_count_lock:
            self._created_connections += cnt

    def check_pid(self):
        if self.pid != os.getpid():
            with self._check_lock:
                if self.pid == os.getpid():
                    # another thread already did the work while we waited
                    # on the lock.
                    return
                self.disconnect()
                self.reset()
            pass
        return

    def get_connection(self):
        """ 
        :rtype: Connection
        """
        self.check_pid()

        try:
            conn = self._available_connections.pop()
        except IndexError:
            conn = self.make_connection()

        log_debug("get connection  connection_count = %s, conn = %s",
                  self._created_connections, conn)
        return conn

    def make_connection(self):
        conn = Connection(**self.connection_args)
        conn.pid = self.pid
        self._atom_increment_created_count(1)

        log_debug("make  connection  connection_count = %s, conn = %s",
                  self._created_connections, conn)
        return conn

    def release(self, connection, can_reuse=None):
        self.check_pid()
        if connection.pid != self.pid:
            return
        if can_reuse is False:
            self._atom_increment_created_count(-1)
        else:
            self._available_connections.append(connection)

        log_debug("release connection , can_reuse = %s, connection_count = %s, conn = %s",
                  can_reuse, self._created_connections, connection)
        pass

    def disconnect(self):
        all_conns = chain(self._available_connections, )
        for connection in all_conns:
            try:
                connection.close()
            except (Exception,):
                pass
        return

    pass
