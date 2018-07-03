#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
from firewdip.sepcial_edit import unock_count
from celery.schedules import crontab


'''
切换开发环境和正式环境
'''


class Config(object):
    COMPARE_SERVER_DEFAULT= True
    BABEL_DEFAULT_LOCALE='zh_CN'
    SECRET_KEY = '##!@5583a5680a59a03d57a42793dae2d523@!$%'
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
                                    'log-3m': {
                                        'task': 'firewdip.task.produce_ip_file',
                                        "schedule": timedelta(minutes=1),
                                                         },
                    #                 'task_3m': {
                    #                     'task': 'firewdip.task.icgoo_visit_detail',
                    #                     "schedule": timedelta(minutes=3),
                    #                 },
                                     'task_1day':{
                                            'task':'firewdip.task.init_today_search_times',
                                                "schedule": crontab(hour=0, minute=1),
                                                                     },
                                     'task_1month':{
                                                'task':'firewdip.task.update_geoip_database',
                                                "schedule": crontab(hour=6,minute=10,),
                                         },
                                                                        }


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:asdasd@192.168.0.6/a_chenwm_fwdip?charset=utf8'
    CELERY_BROKER_URL = 'redis://:123@192.168.0.7:6379/10'
    CELERY_RESULT_BACKEND = 'redis://:123@192.168.0.7:6379/10'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI ='mysql://root:asdasd@192.168.0.6/a_chenwm_fwdip?charset=utf8'
    CELERY_BROKER_URL = 'redis://:123@192.168.0.7:6379/10'
    CELERY_RESULT_BACKEND = 'redis://:123@192.168.0.7:6379/10'


class UseConfig(DevelopmentConfig):
    pass   # 修改此处切换生产环境和开发环境