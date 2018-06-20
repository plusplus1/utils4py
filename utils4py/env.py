#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

__DEBUG_ENV_KEY__ = "IS_DEBUG"
__IS_DEBUG__ = False
__HAS_SET_DEBUG__ = False


def set_debug(debug):
    global __IS_DEBUG__, __HAS_SET_DEBUG__
    if not __HAS_SET_DEBUG__:
        __IS_DEBUG__ = debug
        __HAS_SET_DEBUG__ = True
    return


def is_debug():
    if __HAS_SET_DEBUG__:
        return __IS_DEBUG__
    return os.getenv(__DEBUG_ENV_KEY__, "0") == "1"
