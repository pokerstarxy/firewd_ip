#!/usr/bin/env python
#coding=utf8
from __future__ import absolute_import
from config import UseConfig
from  celery import  Celery
from  firewdip.firewd_ip import app
from firewdip.database import  db_session
from  firewdip.models import VISIT,IPINFO
from sqlalchemy import func
import datetime




def make_celery(app):
    celery = Celery(
    app.import_name,
    broker=UseConfig.CELERY_BROKER_URL,
    backend=UseConfig.CELERY_RESULT_BACKEND
    )
    celery.conf.update(app.config)
    Taskbase=celery.Task
    class ContextTask(Taskbase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return Taskbase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)


@celery.task()
def my_task():
    print 'test celery'


@celery.task()
def ip_limit_rate():
    '''
    每分钟只有一个任务
    1小时执行60个任务
    ---正常规则---
    :return:
    '''
    minute_value=datetime.datetime.now().minute
    while True:
        excute_time=excute_time_list.pop()
        if not minute_value%excute_time:
            break
    str_time='rate_{}m'.format(str(excute_time))
    lock_str='lock_{}m_times'.format(str(excute_time))
    NOW=datetime.datetime.now()
    timestr_count_list=db_session.query(VISIT.ip_detail_id.label('ip_id'),
                                        func.count(VISIT.ip_detail_id).label('count_time')).filter(
                            VISIT.query_time.between(NOW - datetime.timedelta(minutes=timestr), NOW)).group_by(
                            VISIT.ip_detail_id)
    #timestr分钟查询次数按ip分组，有无用户名都锁住，解锁按制定规则来
    for each in timestr_count_list:
        ip_obj= IPINFO.query.get(each.ip_id)
        rate_time=getattr(ip_obj.ip_area,str_time)
        if each.count_time>rate_time:
            #配置锁定状态，增加锁定次数
            getattr(ip_obj,lock_str)+=1
            if not each.ip_white()
                ip_obj.lock_status=1
                db_session.commit()


@celery.task()
def unlock_after_lock(count):
    """
    特定规则,下发IP
    """
    too_much_unlock =IPINFO.query.filter(IPINFO.unlock_after_lockd>count)
    for  each  in too_much_unlock:
        if not each.ip_white():  #如果不是白名单
            each.white_list_status='1'
            each.lock_status=1



@celery.task()
def  produce_ip_file():
    """
    每三分钟下发最新IP，如果文件没发生改变就无操作
    :return:
    """
    pass




















