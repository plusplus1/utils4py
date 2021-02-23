#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

import utils4py.text

__all__ = ['SqlMixin']


def _stringify(v):
    return utils4py.text.TextUtils.to_string(v)


class SqlMixin(object):
    """sql mixin"""

    @staticmethod
    def prepare_select_sql(table_name, fields=None, where_map=None, appends=None, limit=None):
        """
        :param str table_name:
        :param list fields:
        :param dict where_map:
        :param list appends:
        :param int|list  limit:
        :return:
        """
        if fields:
            if isinstance(fields, (list, tuple)):
                str_fields = ','.join(fields)
            else:
                assert isinstance(fields, six.string_types)
                str_fields = _stringify(fields)
        else:
            str_fields = '*'

        sql = ['SELECT {} FROM {}'.format(str_fields, table_name)]
        vs = []
        if where_map:
            assert isinstance(where_map, dict)
            ks = list(where_map.keys())
            sql.append('WHERE')
            sql.append(' AND '.join([k + '%s' for k in ks]))
            vs.extend([where_map[k] for k in ks])
            pass

        if appends:
            if isinstance(appends, six.string_types):
                sql.append(_stringify(appends))
            else:
                assert isinstance(appends, (list, tuple))
                sql.extend(appends)

        if limit:
            sql.append('LIMIT')
            if isinstance(limit, int):
                sql.append('%s')
                vs.append(limit)
            else:  # number, offset
                assert isinstance(limit, (list, tuple)) and 0 < len(limit) < 3
                sql.append(','.join(['%s' for _ in limit]))
                vs.extend(limit)

        return ' '.join(sql), tuple(vs)

    @staticmethod
    def prepare_update_sql(table_name, set_map, where_map):
        """
        :param str table_name:
        :param dict set_map:
        :param dict where_map:
        :return:
        """
        sql = ['UPDATE `{}` SET'.format(table_name)]
        ks = list(set_map.keys())
        vs = [set_map[k] for k in ks]
        sql.append(','.join(["`{}`=%s".format(k) for k in ks]))
        ws = list(where_map.keys())
        vs.extend([where_map[k] for k in ws])
        sql.append('WHERE ' + ' AND '.join(["{}%s".format(k) for k in ws]))
        return " ".join(sql), tuple(vs)

    @staticmethod
    def prepare_insert_sql(table_name, value_map):
        """
        :param str table_name:
        :param dict value_map:
        :return:
        """
        sql = ['INSERT INTO `{}`'.format(table_name)]
        ks = list(value_map.keys())
        vs = [value_map[k] for k in ks]

        sql.append('({})'.format(','.join(['`{}`'.format(x) for x in ks])))
        sql.append('VALUES ({})'.format(','.join(['%s' for _ in ks])))
        return " ".join(sql), tuple(vs)
