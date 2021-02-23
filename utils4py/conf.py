#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import yaml
from six.moves import configparser

from utils4py.env import env


class ConfUtils(object):
    """
        Config utilities
    """

    __conf_dir__ = "conf"
    __conf_test_dir__ = "conf_test"

    @classmethod
    def get_base_dir(cls):
        if env.is_debug:
            return os.path.abspath(os.path.join(os.getcwd(), cls.__conf_test_dir__))
        return os.path.abspath(os.path.join(os.getcwd(), cls.__conf_dir__))

    @classmethod
    def complete_path(cls, relative_path):
        return os.path.abspath(os.path.join(cls.get_base_dir(), relative_path))

    @classmethod
    def _new_parser(cls):
        """
            new parser
        """
        p = configparser.ConfigParser()
        p.optionxform = lambda x: x
        return p

    @classmethod
    def load_parser(cls, config_file):
        """
        :param str config_file:
        :rtype: ConfigParser.ConfigParser
        """
        filename = config_file
        if not str.startswith(config_file, "/"):
            filename = cls.complete_path(config_file)

        parser = cls._new_parser()
        parser.read(filename)
        return parser

    @classmethod
    def load_yaml(cls, config_file):
        filename = config_file
        if not str.startswith(config_file, "/"):
            filename = cls.complete_path(config_file)

        with open(filename) as in_stream:
            return yaml.safe_load(in_stream)


pass
