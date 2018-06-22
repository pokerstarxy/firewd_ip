#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
切换开发环境和线上环境
'''
from datetime import timedelta
from firewdip.sepcial_edit import unock_count

class Config(object):
    # SCHEDULER_API_ENABLED = True
    CELERY_BROKER_URL = 'redis://:icgoo123@192.168.0.7:6379/10'
    CELERY_RESULT_BACKEND = 'redis://:icgoo123@192.168.0.7:6379/10'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_IMPORTS = ("firewdip.task",)
    CELERYBEAT_SCHEDULE = {
        'log-1m': {
            'task': 'firewdip.task.ip_limit_rate',
            # 定时每隔3秒执行（第一种）
            "schedule": timedelta(minutes=1),
            # 定时每天17点-23点，每隔1分钟执行（第2种）
            # "schedule": crontab(minute='*/1',hour='17-23'),
        },
        'log-2m': {
            'task': 'firewdip.task.unlock_after_lock',
            "schedule": timedelta(minutes=2),
            "args": (unock_count,)
        }

        'log-3m': {
            'task': 'firewdip.task.produce_ip_file',
            "schedule": timedelta(minutes=3),
        }
    }


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URI = ''   #redis


class DevelopmentConfig(Config):
    DEBUG = True
    # DEBUG = False
    # DATABASE_URI ='mysql://root:171024@127.0.0.1/fwdip'
    DATABASE_URI ='mysql://root:asdasd@192.168.0.6/a_chenwm_fwdip'


class UseConfig(DevelopmentConfig):
    # 修改此处切换生产环境和开发环境
    pass

