#!/usr/bin/env python
# -*- coding: utf-8 -*-

import models,datetime
from database import  db_session
from sqlalchemy import func

def get_ip(timestr):
    with open('aaa.txt','w+') as f:
        f.writelines('haha')
    print 123
    str_time='rate_{}m'.format(timestr)
    lock_str='lock_{}m_times'.format(timestr)
    NOW=datetime.datetime.now()
    timestr_count_list=db_session.query(models.VISIT.ip_detail_id.label('ip_id'),
                                        func.count(models.VISIT.ip_detail_id).label('count_time')).filter(models.VISIT.query_time.between(NOW - datetime.timedelta(minutes=timestr),NOW)).group_by(models.VISIT.ip_detail_id)
    #timestr分钟查询次数按ip分组
    for each in timestr_count_list:
        ip_obj=models.IPINFO.query.get(each.ip_id)
        rate_time=getattr(ip_obj.ip_area,str_time)
        if each.count_time>rate_time:
            #配置锁定状态，增加锁定次数
            getattr(ip_obj,lock_str)+=1
            ip_obj.lock_status=1
            db_session.commit()

def fwd_rule_one():
    #完全锁定后的解锁次数
    pass


def fwd_rule_two():
    #每天访问次数相差
    pass


def get_black_list():
    fwd_rule_one()
    fwd_rule_two()
    ip_blk_results

