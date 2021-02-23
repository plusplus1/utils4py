#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import os
import platform


class _Env(object):
    """
        环境变量
    """

    _who_am_i = getpass.getuser()
    _system_name = str.lower(platform.system())

    def __init__(self):
        self._is_debug = None
        self._is_docker = None
        self._is_vagrant = None
        self._is_mac_os = None

    @property
    def is_vagrant(self):
        if self._is_vagrant is None:
            self._is_vagrant = (self._who_am_i == 'vagrant')
        return self._is_vagrant

    @property
    def is_mac_os(self):
        if self._is_mac_os is None:
            self._is_mac_os = ('darwin' in self._system_name)
        return self._is_mac_os

    @property
    def is_debug(self):
        if self._is_debug is None:
            if os.path.exists(os.path.join(os.getcwd(), "conf_test")):
                self._is_debug = True
            else:
                try:
                    self._is_debug = True if int(os.environ.get('IS_DEBUG', 0)) == 1 else False
                except (ValueError, KeyError):
                    self._is_debug = False
            pass
        return self._is_debug

    @property
    def is_docker(self):
        if self._is_docker is None:
            self._is_docker = True if os.environ.get('KUBERNETES_PORT', None) else False
        return self._is_docker

    pass


env = _Env()
