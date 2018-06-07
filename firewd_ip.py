# -*- coding: utf-8 -*-
import ipmsg,models,datetime,logging
from  logging.handlers import  SMTPHandler
from flask import Flask
from config import  UseConfig
from flask import request,jsonify
from database import db_session
from werkzeug.contrib.cache import SimpleCache
ADMINS = ['pokerstarxy@sina.com','chenweimeng@dzji.com']
cache=SimpleCache()
app = Flask(__name__)
app.config.from_object(UseConfig)
if   not  app.debug:     #非调试模式运行邮件程序
    mail_handler=SMTPHandler('mail.dzji.com',
                             'sys@dzji.com',ADMINS,'IP_verify faild',
                             credentials=('sys@dzji.com','icgoo2016'))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


@app.route('/')
def hello_world():
    return 'Hello World! This is a flask test'


@app.route('/verify/')
def verify_ip():
    ip=request.args.get('ip')
    logname=request.args.get('logname','Anonymous')
    partno=request.args.get('partno','nothing')
    if all ([ip,logname]):
        logip=ipmsg.Webip(ip)
        ip_obj=models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
        if ip_obj:
            ip_obj.today_times += 1
            ip_obj.total_times += 1
        else:
            ip_addr_info=logip.get_ip_info()
            if not ip_addr_info:      #所有的正常返回均为0
                country_code, city_code, city=logip.ip_info()
                area_id=models.AREA.query.filter_by(country_code=country_code,city_code=city_code).first()
                if area_id:
                    ip_obj=models.IPINFO(ip=ip,logname=logname,ip_log=logip.md5_ip,
                                          area_id=area_id.id,area_info=city,)
                    db_session.add(ip_obj)
                    db_session.commit()
                else:
                    print u'baiduapi出现故障,先让查询,邮件通知管理人员'
                    return 0
        visit_info=models.VISIT(partno=partno,ip_detail_id=ip_obj.id)
        db_session.add(visit_info)
        db_session.commit()
        return jsonify(status=ip_obj.lock_status)
    else:
        #内部调用接口,不对特殊情况返回
        pass


@app.route('/verify_unlock/')
def unlock_ip():
    ip=request.args.get('ip')
    logname=request.args.get('logname','Anonymous')
    logip=ipmsg.Webip(ip)
    ip_obj=models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
    if ip_obj:
        ip_obj.unlock_times+=1
        if logname == 'Anonymous':
            area_obj=models.AREA.query.filter_by(ip_obj.ip_area).first()
            if (ip_obj.lock_1m_times > area_obj.unlock_count_1m) or (ip_obj.lock_30m_times > area_obj.unlock_count_30m):
                # 锁定后解锁的次数
                ip_obj.unlock_after_lockd += 1
                db_session.commit()
                return ip_obj.lock_status
        ip_obj.lock_status=0
        db_session.commit()
        return ip_obj.lock_status
    else:
        return u'木有这个ip'


if __name__ == '__main__':
    app.run()
