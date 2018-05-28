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
    query_time=Column(DateTime)
    ip_detail_id=Column(Integer,ForeignKey('ip_info.id'))

    def __init__(self,partno,ip_detail_id,query_time=datetime.now()):
        self.partno=partno
        self.query_time=query_time
        self.ip_detail_id=ip_detail_id

    def __repr__(self):
        return  self.partno


class IPINFO(Base):
    __tablename__='ip_info'
    id=Column(Integer,primary_key=True,autoincrement=True)
    ip=Column(String(16))
    logname=Column(String(11))
    ip_log=Column(CHAR(32),index=True,unique=True)
    lock_1m_times=Column(SMALLINT)
    lock_30m_times=Column(SMALLINT)
    area_id=Column(Integer, ForeignKey('ip_code_info.id'))
    area_info = Column(String(30), )
    today_times=Column(SMALLINT)
    total_times =Column(Integer)
    lock_status=Column(CHAR(1))
    white_list_status=Column(CHAR(1))
    unlock_times=Column(Integer)
    unlock_after_lockd=Column(SMALLINT)
    create_time=Column(DateTime)
    lastest_time=Column(TIMESTAMP)
    ip_detail_id = relationship('VISIT', backref='ip_detail',lazy='dynamic')

    def __init__(self,ip,logname,ip_log,area_id,area_info,
                 lock_status=0,white_list_status=0,unlock_times=0,
                 lock_1m_times=0,lock_30m_times=0,today_times=1,total_times=1,unlock_after_lockd=0,
                 create_time=datetime.now(),lastest_time=datetime.now()):
        self.ip=ip
        self.logname=logname
        self.ip_log=ip_log
        self.lock_1m_times=lock_1m_times
        self.lock_30m_times=lock_30m_times
        self.area_id=area_id
        self.area_info=area_info
        self.today_times=today_times
        self.total_times=total_times
        self.lock_status=lock_status
        self.white_list_status=white_list_status
        self.unlock_times=unlock_times
        self.unlock_after_lockd=unlock_after_lockd
        self.create_time=create_time
        self.lastest_time=lastest_time

    def get_black_info(self):
        return (self.ip,
                self.white_list_status)

    def __repr__(self):
        return self.ip


# class UNLOCk(Base):
#     __tablename__='ip_rate_limit'
#     id=Column(Integer, primary_key=True,autoincrement=True)
#     time_value=Column(CHAR(3))
#     rate=Column(String(4))
#     unlock_time=Column(String(4))
#     rate_ipseg=Column(String(6))
#
#     def __init__(self,time_value,rate,unlock_time,rate_ipseg):
#         self.time_value=time_value
#         self.rate=rate
#         self.unlock_time=unlock_time
#         self.rate_ipseg=rate_ipseg
#
#     def __repr__(self):
#         return self.__tablename__


class AREA(Base):
    '''
    依照地区  对应不用的标准值  (配置)
    '''
    __tablename__='ip_code_info'
    id=Column(Integer, primary_key=True,autoincrement=True)
    country_code=Column(String(3))
    city_code=Column(SMALLINT)
    rate_1m=Column(SMALLINT)
    rate_30m=Column(SMALLINT)
    rate_ipseg_30m=Column(SMALLINT)
    unlock_count_1m=Column(SMALLINT)
    unlock_count_30m=Column(SMALLINT)
    area_limit_id = relationship('IPINFO', backref='ip_area', lazy='dynamic')

    def __init__(self,country_code,city_code,rate_1m=5,rate_30m=100,rate_ipseg_30m=200,
                 unlock_count_1m=6,unlock_count_30m=3):
        self.country_code=country_code
        self.city_code=city_code
        self.rate_1m=rate_1m
        self.rate_30m=rate_30m
        self.rate_ipseg_30m=rate_ipseg_30m
        self.unlock_count_1m=unlock_count_1m
        self.unlock_count_30m=unlock_count_30m

    def __repr__(self):
        return  self.country_code


class IPSEG(Base):
    __tablename__='ip_ipseg_info'
    id=Column(Integer, primary_key=True,autoincrement=True)
    ip=Column(String(12))
    ipseg=Column(CHAR(32),unique=True,index=True)    #md5
    ipseg_status=Column(CHAR(1))
    create_time=Column(DateTime)

    def __init__(self,ip,ipseg,ipseg_status=1,create_time=datetime.now()):
        self.ip = ip
        self.ipseg = ipseg
        self.ipseg_status = ipseg_status
        self.create_time = create_time

    def __repr__(self):
        return self.ip

