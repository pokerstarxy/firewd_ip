# -*- coding: utf-8 -*-
import ipmsg,models
import logging
from logging.handlers import  SMTPHandler
from flask import Flask,request,jsonify
from config import  UseConfig
from database import db_session
from sepcial_edit import  white_country_list
from flask_admin import Admin
from homepage import MyView,IPModelView,IpAreaView,IpSegModelView

ADMINS = ['chenweimeng@dzji.com']
# ADMINS = ['pokerstarxy@sina.com','chenweimeng@dzji.com']


def create_app():
    app = Flask(__name__)
    app.config.from_object(UseConfig)
    admin=Admin(app)
    admin.add_view(MyView(name='IpSet'))
    admin.add_view(IPModelView(models.IPINFO,db_session))
    admin.add_view(IpAreaView(models.AREA,db_session))
    admin.add_view(IpSegModelView(models.IPSEG,db_session))
    if   not  app.debug:     #非调试模式 运行邮件程序
        mail_handler = SMTPHandler('mail.qq.com',
                                   'sys@qq.com', ADMINS, 'IP_verify code BUG',
                                   credentials=('qq@qq.com', 'co2016'))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    return app


app=create_app()


@app.route('/')
def hello_world():
    from firewdip.task import my_task
    my_task.delay()
    return 'Hello World! This is a flask test'


@app.route('/verify/')
def verify_ip():
    ip=request.args.get('ip')
    logname=request.args.get('logname','Anonymous')
    partno=request.args.get('partno','nothing')
    if all ([ip,logname]):
        logip= ipmsg.Webip(ip,logname)
        ip_obj= models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
        if ip_obj:
            ip_obj.today_times += 1
            ip_obj.total_times += 1
        else:
            try:
                throw_flag=1
                ip_addr_info=logip.get_ip_info()
            except RuntimeError:
                return jsonify(status=0)                 #'baiduapi出现故障,先让查询,邮件通知管理人员'
            else:
                throw_flag=0
                if not ip_addr_info:      #正常返回为0
                    country_code, city_code, city=logip.ip_info()
                    area_id= models.AREA.query.filter_by(country_code=country_code, city_code=city_code).first()
                    if not area_id:
                        area_id= models.AREA(country_code=country_code, city_code=city_code)
                        db_session.add(area_id)
                        db_session.commit()
                    ip_lock_status = 1 if country_code not in white_country_list else 0
                    ip_obj= models.IPINFO(ip=ip, logname=logname, ip_log=logip.md5_ip,
                                          area_id=area_id.id, area_info=city,lock_status=ip_lock_status )
                    db_session.add(ip_obj)
                    db_session.commit()
            finally:
                if throw_flag:
                    raise
        visit_info= models.VISIT(partno=partno, ip_detail_id=ip_obj.id,lock_flag=ip_obj.lock_status)
        db_session.add(visit_info)
        db_session.commit()
        return jsonify(status=ip_obj.lock_status)


@app.route('/verify_unlock/')
def unlock_ip():
    ip=request.args.get('ip')
    logname=request.args.get('logname','Anonymous')
    logip= ipmsg.Webip(ip,logname)
    ip_obj= models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
    if ip_obj:
        ip_obj.unlock_times+=1
        if logname == 'Anonymous':
            area_obj= models.AREA.query.filter_by(id=ip_obj.area_id).first()
            if (ip_obj.lock_1m_times > area_obj.lock_max_1m) or (ip_obj.lock_30m_times > area_obj.lock_max_30m):
            # 锁定后解锁的次数，只针对非登录用户
                ip_obj.unlock_after_lockd += 1
                db_session.commit()
                return jsonify(status=ip_obj.lock_status)
        ip_obj.lock_status=0
        ip_obj.unlock_after_lockd=0
        db_session.commit()
        return jsonify(status=ip_obj.lock_status)
    else:
        return u'木有这个ip'


@app.route('/test/')
def test_mail():
    """
    测试程序内部错误出发邮件
    :return:
    """
    print 'ab%s' %(1,2,3)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """关闭数据库链接"""
    db_session.remove()




