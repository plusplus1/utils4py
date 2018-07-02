#!/usr/bin/env python
# -*- coding: utf-8 -*-


from utils4py.data.cache import SimpleQueue as RedisQueue
from utils4py.data.cache import connect as connect_redis
from utils4py.data.mysql import connect as connect_mysql
from utils4py.data.mongo import connect as connect_mongo
