# -*- coding: utf-8 -*-
import logging,ipmsg,models,datetime
from flask import Flask
from flask import request,jsonify
from config import UseConfig
from database import db_session
from flask_apscheduler import APScheduler
import flask_restful,flask_mail,flask_cache
from logging.handlers import SMTPHandler
from logging import getLogger
from logging import Formatter
app = Flask(__name__)


# cache.init_app(app)
# ADMINS = ['yourname@example.com']
# if not app.debug:
#     mail_handler = SMTPHandler('127.0.0.1',
#                                'server-error@example.com',
#                                ADMINS, 'YourApplication Failed')
#     mail_handler.setLevel(logging.ERROR)
#     mail_handler.setFormatter(Formatter('''
#     Message type:       %(levelname)s
#     Location:           %(pathname)s:%(lineno)d
#     Module:             %(module)s
#     Function:           %(funcName)s
#     Time:               %(asctime)s
#
#     Message:
#
#     %(message)s
#     '''))
#     app.logger.addHandler(mail_handler)
#     loggers = [app.logger, getLogger('sqlalchemy'),
#                getLogger('mail')]
#     for logger in loggers:
#         logger.addHandler(mail_handler)
app.config.from_object(UseConfig)


@app.route('/')
def hello_world():
    return 'Hello World!'


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
            #添加设置缓存
            #添加最后一次解锁成功的时间
            area_obj=models.AREA.query.filter_by(ip_obj.ip_area).first()
            if (ip_obj.lock_1m_times > area_obj.unlock_count_1m) or (ip_obj.lock_30m_times > area_obj.unlock_count_30m):
                return ip_obj.lock_status
        ip_obj.lock_status=0
        db_session.commit()
        return ip_obj.lock_status
    else:
        return u'木有这个ip'


if __name__ == '__main__':
    schetask = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run()



# @app.teardown_request
# def shutdown_session(exception=None):
#     db_session.remove()