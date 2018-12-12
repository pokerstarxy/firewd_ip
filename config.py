#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
from firewdip.sepcial_edit import unock_count
from celery.schedules import crontab


'''
切换开发环境和正式环境
'''


class Config(object):
    MAIL_SERVER=''
    MAIL_USERNAME=''
    MAIL_PASSWORD=''
    MAIL_DEFAULT_SENDER=''
    ADMIN_CREDENTIALS=('','')
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX='fwdip_key'
    CACHE_DEFAULT_TIMEOUT=5
    COMPARE_SERVER_DEFAULT= True
    BABEL_DEFAULT_LOCALE='zh_CN'
    SECRET_KEY = '##!@83680a59a03d7a42793dae25656d523@!$%'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    CELERY_TASK_RESULT_EXPIRES = 3600
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_IMPORTS = ("firewdip.task",)
    CELERYBEAT_SCHEDULE = {
                                    'log-1m': {
                                        'task': 'firewdip.task.ip_limit_rate',
                                        "schedule": timedelta(minutes=1),
                                        # 定时每天17点-23点，每隔1分钟执行（第2种）
                                        # "schedule": crontab(minute='*/1',hour='17-23'),
                                                            },
                                    'log-2m': {
                                        'task': 'firewdip.task.unlock_after_lock',
                                        "schedule": timedelta(minutes=1),
                                        "args": (unock_count,)
                                                            },
                                    'task_5m': {
                                        'task': 'firewdip.task.tt_visit_detail',
                                        "schedule": timedelta(minutes=5),
                                    },
                                        'task_2h': {
                                            'task': 'firewdip.task.up_ip_info',
                                            "schedule": timedelta(hours=2),
                                        },
                                    'task_1day':{
                                            'task':'firewdip.task.init_today_search_times',
                                         #和时区有关   --东八区匹配早上0点改为16点
                                                "schedule": crontab(hour=16, minute=1),
                                                                     },
                                    'task_1month':{
                                                'task':'firewdip.task.update_geoip_database',
                                                "schedule": crontab(hour=6,minute=10,),
                                         },
                                                                        }


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:tttt@192.168.0.6/fwdip?charset=utf8'
    CELERY_BROKER_URL = 'redis://:pwd123@192.168.0.7:6379/10'
    CELERY_RESULT_BACKEND = 'redis://:pwd@192.168.0.7:6379/10'
    CACHE_REDIS_HOST = '192.168.0.7'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = ''
    CACHE_REDIS_PASSWORD = 'kk123'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:tttt@192.168.0.6/fwdip?charset=utf8'
    CELERY_BROKER_URL = 'redis://:pwd123@192.168.0.7:6379/10'
    CELERY_RESULT_BACKEND = 'redis://:pwd@192.168.0.7:6379/10'
    CACHE_REDIS_HOST = '192.168.0.7'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = ''
    CACHE_REDIS_PASSWORD = 'kk123'


class UseConfig(DevelopmentConfig):
    pass   # 修改此处切换生产环境和开发环境