#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import flask
from gevent.pywsgi import WSGIServer

from utils4py.env import env
from utils4py.flask_ext.interceptor import init_interceptors
from utils4py.flask_ext.routes import init_routes

_logger = logging.getLogger(__name__)


class AppServer(object):
    """
       App server
    """
    flask_init_conf = {}
    interceptor_packages = ["utils4py.flask_ext.interceptor"]
    route_packages = []

    def __init__(self, app_name, logger):
        self._app_name = app_name
        self._logger = logger
        self._app = None
        self._debug = env.is_debug
        pass

    def _init_app(self):
        app = flask.Flask(self._app_name, **self.flask_init_conf)
        setattr(app, "_logger", self._logger)

        init_interceptors(app, paths=self.interceptor_packages, logger=self._logger)
        init_routes(app, paths=self.route_packages)

        if self._debug:
            app.config["DEBUG"] = True

        self._app = app
        return app

    @property
    def app(self):
        """
        :rtype: flask.Flask
        """
        if not self._app:
            self._init_app()
        return self._app

    def run(self, port):
        _logger.info("Start server, port=%s, debug=%s", port, self._debug)
        self.app.run(host='0.0.0.0', port=port)
        pass

    def run_wsgi(self, port):
        _logger.info("Start wsgi server, port=%s, debug=%s", port, self._debug)
        server = WSGIServer(('', port), self.app)
        server.serve_forever()

    pass
