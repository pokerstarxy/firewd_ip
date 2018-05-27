#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  models,datetime
from database import  db_session

# def get_ip(timestr):
#     str_time='rate_{}m'.format(timestr)
#     NOW=datetime.datetime.utcnow()
#     #筛选分组查询实现？
#     timestr_count_list=models.VISIT.query.group_by(models.VISIT.ip_detail_id).all()
#     # filter_by(query_time.between(NOW - datetime.timedelta(minutes=1), NOW))
#     for each in timestr_count_list:
#         if each.count>each.ip_detail.ip_area.rate_1m:
#             #属性测试,配置锁定状态，增加锁定次数
#             pass
#         else:
#             pass


