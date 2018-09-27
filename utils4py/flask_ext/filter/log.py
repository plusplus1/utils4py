#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time

from flask import g, request

from utils4py import TextUtils
from utils4py.flask_ext.filter import BaseFilter


class Filter(BaseFilter):
    """
        Log filters
    """

    IGNORE_LOG_REQUEST_PATH = set([])

    @classmethod
    def _format_kv(cls, kv_log):
        """
        :param kv_log:
        :return:
        """
        return "\t".join(map(
            lambda x: "{}={}".format(*x),
            [(k, TextUtils.to_string(kv_log[k])) for k in sorted(kv_log.keys())]
        ))

    def before_request(self, *args, **kwargs):

        g.req_timer = {'start': time.time(), 'end': 0, 'cost': 0, }

        g.method = request.method
        g.path = request.path
        g.remote_ip = request.headers.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)

        params = dict()
        params.update({k: request.args[k] for k in request.args.keys()} if request.args else {})
        params.update({k: request.form[k] for k in request.form.keys()} if request.form else {})

        if request.data:
            try:
                json_params = request.get_json()
                if not json_params:
                    json_params = json.loads(request.get_data())
                if json_params and isinstance(json_params, dict):
                    params.update(json_params)
            except (Exception,):
                pass

        g.params = params
        g.code = 0
        g.kv_log = dict()
        return

    def after_request(self, *args, **kwargs):

        path = g.path
        if path and self.IGNORE_LOG_REQUEST_PATH and path in self.IGNORE_LOG_REQUEST_PATH:
            return

        g.req_timer['end'] = time.time()
        g.req_timer['cost'] = round(1000 * (g.req_timer['end'] - g.req_timer['start']), 2)

        log_data = {
            'method'   : g.method,
            'remote_ip': g.remote_ip,
            'path'     : g.path,
            'code'     : g.code,
            'cost'     : g.req_timer['cost'],
        }
        if g.kv_log and isinstance(g.kv_log, dict):
            for k, v in g.kv_log.items():
                if k not in log_data:
                    log_data[k] = v
            pass

        self.logger.info(self._format_kv(log_data))
        pass

    pass


pass
