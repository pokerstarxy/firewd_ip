#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
切换开发环境和线上环境
'''


class Config(object):
    JOBS = [
        {
            'id': 'get_ip_ban1',
            'func': 'crontask:get_ip',
            'args': 1,
            'trigger': 'interval',
            'seconds': 1 * 30
        },
        {
            'id': 'get_ip_ban30',
            'func': 'crontask:get_ip',
            'args': 30,
            'trigger': 'interval',
            'seconds': 30 * 60
        },
        {
            'id': 'get_black_list',
            'func': 'crontask:get_black_list',
            'args': None,
            'trigger': 'interval',
            'seconds': 60 * 60
        },
    ]
    SCHEDULER_API_ENABLED = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = ''


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI ='mysql://root:171024@127.0.0.1/fwdip'


class UseConfig(DevelopmentConfig):
    # 修改此处切换生产环境和开发环境
    pass

