#!/usr/bin/env python
#coding=utf8
import os
"""以下是后台编辑的数据"""
#获取列表时间段的ip访问次数
excute_time_list = [1, 30]

#被锁定后解锁次数达到10次 且未解开锁
unock_count=10

#国外ip先锁定一次
white_country_list=['CN','HK','XXX']


#ip 状态码
sql_results = {
    '0': (0, 0, 0, '8', 0),
    '1': (0, 0, 0, '0', 0),
    '2': (12345, 12345, 1, '0', 0),
    '3': (12345, 12345, 1, '9', 0),
    '4': (1,),
    '5': (0,),
}

#两次查询间隔时间   --不能设置为0
timelimit=1



base_dir=os.path.dirname(os.path.abspath(__file__))
dropfile_name='ip_fwd_drop.txt'
rdtfile_name='ip_fwd_rdt.txt'
white_name='ip_fwd_white.txt'
path_file_drop=os.path.join(base_dir,dropfile_name)
path_file_redirect=os.path.join(base_dir,rdtfile_name)
path_file_white=os.path.join(base_dir,white_name)