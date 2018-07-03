#!/usr/bin/env python
#coding=utf8
from database import  db_session
from firewdip.models import *
from sqlalchemy import func
import datetime

NOW = datetime.datetime.now()
print NOW
count=5
c=IPINFO.query.filter(IPINFO.white_list_status=='9').all()
print c
d=db_session.query(VISIT.ip_detail_id.label('ip_id'),
                                        func.count(VISIT.ip_detail_id).label('count_time')).filter(
                            VISIT.query_time.between(NOW - datetime.timedelta(minutes=1), NOW)).group_by(
                            VISIT.ip_detail_id).all()
print d