#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
切换开发环境和线上环境
'''


class Config(object):

    # SCHEDULER_API_ENABLED = True
    pass

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DATABASE_URI = ''   #redis


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    # DATABASE_URI ='mysql://root:171024@127.0.0.1/fwdip'
    DATABASE_URI ='mysql://root:asdasd@192.168.0.6/a_chenwm_fwdip'


class UseConfig(DevelopmentConfig):
    # 修改此处切换生产环境和开发环境
    pass

