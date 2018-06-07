#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
数据库初始化操作以及配置
'''


import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import UseConfig
from models import *
engine = create_engine(UseConfig.DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
    print u'创建数据库完成'


def drop_db():
    chocie=raw_input(u'确定要删除数据库? Y/N')
    chocie=chocie.upper()
    if chocie == 'Y':
        Base.metadata.drop_all(bind=engine)
        print u'数据库删除完毕.可以跑路了'
    else:
        print u'未执行操作,正常退出,请确定你的输入....'


def test():
    print 123


if __name__=='__main__':
    para=sys.argv[1]
    import database
    func=getattr(database,para)
    func()
