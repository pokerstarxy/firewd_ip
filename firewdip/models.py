#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库结构模型
"""
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column,CHAR,Integer,ForeignKey,DateTime,String,TIMESTAMP,SMALLINT


class VISIT(Base):
    __tablename__ = 'ip_visit_log'
    id=Column(Integer, primary_key=True,autoincrement=True)
    partno=Column(String(30),)
    lock_flag=Column(SMALLINT)
    query_time=Column(DateTime,default=datetime.now)
    ip_detail_id=Column(Integer,ForeignKey('ip_info.id'))

    def __init__(self,partno,ip_detail_id,lock_flag):
        self.partno=partno
        self.lock_flag=lock_flag        #统计有效查询次数
        self.ip_detail_id=ip_detail_id  #ip_info 主键

    def __repr__(self):
        return  self.partno


class IPINFO(Base):
    __tablename__='ip_info'
    id=Column(Integer,primary_key=True,autoincrement=True)
    ip=Column(String(16))
    logname=Column(String(11))
    ip_log=Column(CHAR(32),index=True,unique=True)   #MD5 ip+logname
    lock_1m_times=Column(SMALLINT,default=0)     #1m锁定次数
    lock_30m_times=Column(SMALLINT,default=0)
    area_id=Column(Integer, ForeignKey('ip_code_info.id'))  #地区信息
    area_info = Column(String(30), )
    today_times=Column(SMALLINT,default=1)  #当天查询次数
    total_times =Column(Integer,default=1)
    lock_status=Column(SMALLINT)
    white_list_status=Column(CHAR(1),default=0)     #白名单状态
    unlock_times=Column(Integer,default=0)
    unlock_after_lockd=Column(SMALLINT,default=0)
    create_time=Column(DateTime,default=datetime.now)
    lastest_time=Column(TIMESTAMP,default=datetime.now,onupdate=datetime.now)
    ip_detail_id = relationship('VISIT', backref='ip_detail',lazy='dynamic')

    def __init__(self,ip,logname,ip_log,area_id,area_info,lock_status,):
        self.ip=ip
        self.logname=logname
        self.ip_log=ip_log
        self.area_id=area_id
        self.area_info=area_info
        self.lock_status=lock_status

    def has_logname(self):
        return self.logname!='Anonymous'

    def  ip_white(self):
        """
        白名单 code 8
        黑名单 code 9

        :return:
        """
        return self.white_list_status=='8'

    def __repr__(self):
        return self.ip


class AREA(Base):
    '''
    依照地区  对应不用的标准值  (配置)
    '''
    __tablename__='ip_code_info'
    id=Column(Integer, primary_key=True,autoincrement=True)
    country_code=Column(String(3))  #国家编码
    city_code=Column(SMALLINT)    #城市编码  --国外为0
    rate_1m=Column(SMALLINT,default=5)             #一分钟访问次数
    rate_30m=Column(SMALLINT,default=100)
    rate_ipseg_30m=Column(SMALLINT,default=200)
    lock_max_1m=Column(SMALLINT,default=6)      #锁定次数大于此数字不让解锁
    lock_max_30m=Column(SMALLINT,default=3)
    area_limit_id = relationship('IPINFO', backref='ip_area', lazy='dynamic')

    def __init__(self,country_code,city_code,):
        self.country_code=country_code
        self.city_code=city_code

    def __repr__(self):
        return  ('%s-%s') %(self.country_code,self.city_code)


class IPSEG(Base):
    __tablename__='ip_ipseg_info'
    id=Column(Integer, primary_key=True,autoincrement=True)
    ip=Column(String(12))
    ipseg=Column(CHAR(32),unique=True,index=True)    #md5
    ipseg_status=Column(SMALLINT,default=1)
    create_time=Column(DateTime,default=datetime.now)

    def __init__(self,ip,ipseg,):
        self.ip = ip
        self.ipseg = ipseg

    def __repr__(self):
        return self.ip

