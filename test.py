#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import AREA,IPSEG,IPINFO,VISIT
from database import db_session

# u=AREA('CN','222')
# u=IPINFO(ip='1222',logname='asdasd',area_id=1,area_info='北京',ip_log='asdasdasdasdxxx')
# u=IPSEG(ip='13333',ipseg='ghgh')
# u=VISIT(partno='ref02au',ip_detail_id=2)
u=IPINFO.query.filter_by(id='2')
print u
# vv=dict(ip='1222',logname='asdasd',area_id=1,area_info=u'北京',ip_log='asdasdasdasdxxx')
# print vv
# u=VISIT.query.filter_by(id=1).first()
# db_session.add(u)
# db_session.commit()

# print u.ip_detail.ip_log