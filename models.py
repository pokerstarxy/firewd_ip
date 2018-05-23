#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
规则更新ip或者ip段锁定状态
定时任务执行规则去匹配

"""


from firewd_ip import  app
from flask_sqlalchemy import  SQLAlchemy
#sql 配置
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:171024@127.0.0.1/ipfire'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)


class VISIT(db.Model):
    __tablename__ = 'ip_visit_log'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    partno=db.Column(db.string(30),)
    query_time=db.Column(db.datetime,default=datetime.now)
    # ip_detail_id=db.Column(db.Integer,db.ForeignKey())
    ipinfo(ip_detail_id)=

    def __init__(self,id,partno,query_time,ip_detail_id):
        self.id=id
        self.partno=partno
        self.query_time=query_time
        self.ip_detail_id=ip_detail_id


class IPINFO(db.Model):
    __tablename__='ip_info'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    ip=db.Column(db.string(16),nullable=False)
    logname=db.Column(db.string(11),)
    ip_log=db.Column(db.string(32),index=True,unique=True,nullable=False)
    unlock_1m_times=
    unlock_30m_times=
    (AREA)area_id=
    today_times=
    total_times=
    lock_status=
    white_list_status=
    unlock_times=
    create_time=
    lastest_time=


class UNLOCk(db.Model):
    __tablename__='ip_rate_limit'
    id=
    time_value=
    rate_1m=
    # rate_10m=
    rate_30m=
    # rate_60m=
    rate_ipseg=


class AREA(db.Model):
    __tablename__='ip_code_info'
    id=
    country_code=
    city_code=
    unlock(arealimit_id)=


class IPSEG(db.Model):
    __tablename__='ip_ipseg_info'
    id=
    ip=
    ipseg(md5)=
    ipseg_status=
    create_time=


