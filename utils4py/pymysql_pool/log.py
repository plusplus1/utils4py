#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

pool_logger = logging.getLogger("pymsql_pool")


def log_debug(*args, **kwargs):
    if pool_logger:
        pool_logger.debug(*args, **kwargs)


def log_info(*args, **kwargs):
    if pool_logger:
        pool_logger.info(*args, **kwargs)


def log_warn(*args, **kwargs):
    if pool_logger:
        pool_logger.warn(*args, **kwargs)


def log_error(*args, **kwargs):
    if pool_logger:
        pool_logger.error(*args, **kwargs)
