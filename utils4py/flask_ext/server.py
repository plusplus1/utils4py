#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

import flask
from gevent.pywsgi import WSGIServer

import utils4py
from utils4py.flask_ext.filter import init_filters
from utils4py.flask_ext.routes import init_routes


class AppServer(object):
    """
        App Server
    """

    filter_paths = ["utils4py.flask_ext.filter"]
    route_paths = []

    def __init__(self, app_name, logger):
        self._app_name = app_name
        self._logger = logger
        self._app = None
        self._debug = utils4py.env.is_debug()
        pass

    def _init_app(self):
        app = flask.Flask(self._app_name)
        init_filters(app, paths=self.filter_paths, logger=self._logger)
        init_routes(app, paths=self.route_paths)
        setattr(app, "_logger", self._logger)

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
        logging.info("Start server, port=%s, debug=%s", port, self._debug)
        self.app.run(host='0.0.0.0', port=port)
        pass

    def run_wsgi(self, port):
        logging.info("Start wsgi server, port=%s, debug=%s", port, self._debug)
        server = WSGIServer(('', port), self.app)
        server.serve_forever()

    pass
