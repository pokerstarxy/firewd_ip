#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
切换开发环境和线上环境
'''


class Config(object):
    MAIL_SERVER='smtp.sina.com',
    MAIL_PROT=25,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'test_code@sina.com',
    MAIL_PASSWORD = 'pwd@test',
    MAIL_DEBUG = True
    JOBS = [
        {
            'id': 'get_ip_ban',
            'func': 'crontask.get_ip',
            'args': None,
            'trigger': 'interval',
            'seconds': 5 * 60
        }
    ]


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = ''
    # CACHE_TYPE='redis'
    # CACHE_REDIS_HOST='127.0.0.1'
    # CACHE_REDIS_PORT=6379
    # CACHE_REDIS_DB= ''
    # CACHE_REDIS_PASSWORD=''


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI ='mysql://root:171024@127.0.0.1/fwdip'
    # CACHE_TYPE='redis'
    # CACHE_REDIS_HOST='127.0.0.1'
    # CACHE_REDIS_PORT=6379
    # CACHE_REDIS_DB= ''
    # CACHE_REDIS_PASSWORD=''


class UseConfig(DevelopmentConfig):
    # 修改此处切换生产环境和开发环境
    pass

