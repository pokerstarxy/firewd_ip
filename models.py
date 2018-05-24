#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
规则更新ip或者ip段锁定状态
定时任务执行规则去匹配

"""


from firewd_ip import  app
from flask_sqlalchemy import  SQLAlchemy
#sql 配置
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:asdasd@192.168.0.7/chenwm_test'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)


class VISIT(db.Model):
    __tablename__ = 'ip_visit_log'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    partno=db.Column(db.VARCHAR(30),)
    query_time=db.Column(db.DATETIME,default=datetime.now)
    ip_detail_id=db.Column(db.Integer, db.ForeignKey('ip_info.id'))


    # def __init__(self,id,partno,query_time,ip_detail_id):
    #     self.id=id
    #     self.partno=partno
    #     self.query_time=query_time
    #     self.ip_detail_id=ip_detail_id
    def __repr__(self):
        return  self.partno

class IPINFO(db.Model):
    __tablename__='ip_info'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    ip=db.Column(db.VARCHAR(16),nullable=False)
    logname=db.Column(db.VARCHAR(11),)
    ip_log=db.Column(db.CHAR(32),index=True,unique=True,nullable=False)
    lock_1m_times=db.Column(db.VARCHAR(4))
    lock_30m_times=db.Column(db.VARCHAR(4))
    area_id=db.Column(db.Integer, db.ForeignKey('ip_code_info.id'))
    today_times=db.Column(db.Integer,default=0)
    total_times =db.Column(db.Integer,default=0)
    lock_status=db.Column(db.BOOLEAN,default=0)
    white_list_status=db.Column(db.SMALLINT,default=0)
    unlock_times=db.Column(db.Integer,default=0)
    create_time=db.Column(db.DATETIME,default=datetime.now)
    lastest_time=db.Column(db.DATETIME,default=datetime.now)
    ip_detail_id = db.relationship('VISIT', backref='ip_detail',lazy='dynamic')

    def __repr__(self):
        return  self.ip


class UNLOCk(db.Model):
    __tablename__='ip_rate_limit'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    time_value=db.Column(db.CHAR(3))
    rate_1m=db.Column(db.VARCHAR(4))
    # rate_10m=
    rate_30m=db.Column(db.VARCHAR(4))
    # rate_60m=
    rate_ipseg=db.Column(db.VARCHAR(6))

    def __repr__(self):
        return  self.__tablename__


class AREA(db.Model):
    __tablename__='ip_code_info'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    country_code=db.Column(db.VARCHAR(3))
    city_code=db.Column(db.VARCHAR(4))
    area_limit_id = db.relationship('IPINFO', backref='ip_area', lazy='dynamic')

    def __repr__(self):
        return  self.country_code


class IPSEG(db.Model):
    __tablename__='ip_ipseg_info'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    ip=db.Column(db.VARCHAR(12))
    ipseg(md5)=db.Column(db.CHAR(32))
    ipseg_status=db.Column(db.SMALLINT)
    create_time=db.Column(db.DATETIME,default=datetime.now)

    def __repr__(self):
        return  self.ip




db.create_all()