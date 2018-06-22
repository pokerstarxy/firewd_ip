#!/usr/bin/env python
#coding=utf8
"""以下是后台编辑的数据"""
#获取列表时间段的ip访问次数
excute_time_list = [1, 30]

#被锁定后解锁次数达到10次 且未解开锁
unock_count=10

#国外ip先锁定一次
white_country_list=['CN','HK']


"""

"""
# #ip状态码,不同的ip对应不同的状态码,为了隔离对icgoo的影响
# ip_status_code={
#      'white_code':100,
#      'normal_code':200,
#      'verify_code':205,
#      'redirect_code':301,
#      'black_code':403,
# }