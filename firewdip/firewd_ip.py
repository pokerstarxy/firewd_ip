# -*- coding: utf-8 -*-
import ipmsg,models
import logging,datetime,sqlalchemy
from logging.handlers import  SMTPHandler
from flask import Flask,request,jsonify
from flask_mail import Mail,Message
from config import  UseConfig
from database import db_session
from sepcial_edit import  white_country_list,timelimit
from flask_admin import Admin
from homepage import MyView,IPModelView,IpAreaView,IpSegModelView
from flask_caching import Cache
from firewdip.sepcial_edit import sql_results
ADMINS = [
    'a@qq.com',
]


def create_app():
    app = Flask(__name__)
    app.config.from_object(UseConfig)
    app.cache = Cache(app)
    admin=Admin(app)
    admin.add_view(MyView(name='IpSet'))
    admin.add_view(IPModelView(models.IPINFO,db_session))
    admin.add_view(IpAreaView(models.AREA,db_session))
    admin.add_view(IpSegModelView(models.IPSEG,db_session))
    if   not  app.debug:     #非调试模式 运行邮件程序
        mail_handler = SMTPHandler('',
                                   '', ADMINS, 'IP_verify code BUG',
                                   credentials=('', ''))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    return app


app=create_app()
mail=Mail()
mail.init_app(app)


@app.route('/verify/')
def verify_ip():
    ip=request.args.get('ip')
    ip = ip.split(',')[0].strip()
    logname=request.args.get('logname',)
    logname=logname if logname else 'Anonymous'
    partno=request.args.get('partno', )
    partno=partno if partno else 'nothing'
    if 8<datetime.datetime.now().hour<22:
        # 修改次数设置无限制时间
        global_lock_flag=1
    else:
        global_lock_flag=1
    if all ([ip,logname]):
        logip= ipmsg.Webip(ip,logname)
        '''
        取消注释 开启限制同一用户请求间隔时间
        '''
        # if logname == 'Anonymous':
        #     cache_in=app.cache.get(logip.md5_ip)
        #     if cache_in:
        #         return jsonify(locked=1,ip=ip)
        #     else:
        #         #非登录用户每次请求相隔固定时间
        #         app.cache.set(logip.md5_ip,1,timeout=timelimit)
        ip_obj= models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
        # dump_flag = 0
        if ip_obj:
            ip_obj.today_times += 1
            ip_obj.total_times += 1
        else:
            try:
                throw_flag=1
                logip.get_ip_info()
            except RuntimeError:
                return jsonify(locked=0,ip=ip)                 #'baiduapi出现故障,先让查询,邮件通知管理人员'
            else:
                throw_flag=0
                country_code, city_code, city=logip.ip_info()
                area_id= models.AREA.query.filter_by(country_code=country_code, city_code=city_code).first()
                if not area_id:
                    area_id= models.AREA(country_code=country_code, city_code=city_code)
                    db_session.add(area_id)
                    db_session.commit()
                ip_lock_status = 1 if country_code not in white_country_list else 0
                ip_obj= models.IPINFO(ip=ip, logname=logname, ip_log=logip.md5_ip,
                                      area_id=area_id.id, area_info=city,lock_status=ip_lock_status )
                try:
                    db_session.add(ip_obj)
                    db_session.commit()
                except Exception as e:
                    db_session.rollback()
                    #回滚后记录此次查询
                    ip_obj = models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
                    if ip_obj:
                        ip_obj.today_times += 1
                        ip_obj.total_times += 1
                    else:
                        raise  RuntimeError('not get ip obj')
            finally:
                if throw_flag:
                    raise
        if global_lock_flag:
            status_ip=ip_obj.lock_status
        else:
            status_ip=0
        visit_info= models.VISIT(partno=partno, ip_detail_id=ip_obj.id,lock_flag=status_ip)
        db_session.add(visit_info)
        db_session.commit()
        return jsonify(locked=status_ip,ip=ip)
    else:
        raise RuntimeError('wrong requests')


@app.route('/verify_success/')
def unlock_ip():
    ip=request.args.get('ip')
    ip = ip.split(',')[0].strip()
    logname=request.args.get('logname')
    logname=logname if logname else 'Anonymous'
    logip= ipmsg.Webip(ip,logname)
    if 8<datetime.datetime.now().hour<22:
        #修改次数设置无限制时间
        global_lock_flag=1
    else:
        global_lock_flag=1
    ip_obj= models.IPINFO.query.filter_by(ip_log=logip.md5_ip).first()
    if ip_obj:
        ip_obj.unlock_times+=1
        if logname == 'Anonymous':
            area_obj= models.AREA.query.filter_by(id=ip_obj.area_id).first()
            if (ip_obj.lock_1m_times > area_obj.lock_max_1m) or (ip_obj.lock_30m_times > area_obj.lock_max_30m):
            # 锁定后解锁的次数，只针对非登录用户
                ip_obj.unlock_after_lockd += 1
                db_session.commit()
                if global_lock_flag:
                    return jsonify(unlocked=ip_obj.lock_status,ip=ip)
                else:
                    return jsonify(unlocked=0, ip=ip)
        ip_obj.lock_status=0
        ip_obj.unlock_after_lockd=0
        db_session.commit()
        return jsonify(unlocked=0, ip=ip)
    else:
        raise RuntimeError('wrong ip')


@app.route('/block_ip/')
def block_ip():
    ip=request.args.get('ip')
    status_code=request.args.get('level','2')
    ip = ip.split(',')[0].strip()
    ip_str =ipmsg.Webip(ip, 'Anonymous')
    ip_obj = models.IPINFO.query.filter(models.IPINFO.ip_log == ip_str.md5_ip).first()
    if ip_obj:
        if not ip_obj.ip_white():
            (ip_obj.lock_1m_times, ip_obj.lock_30m_times, ip_obj.lock_status,
             ip_obj.white_list_status, ip_obj.unlock_after_lockd) = sql_results[status_code]
    db_session.commit()
    return jsonify(locked=1,ip=ip)


@app.route('/search_history/')
def his_search():
    user_name=request.args.get('username')
    off_set=request.args.get('offset','20')
    skip=request.args.get('skip','0')    #skip+offset  类似mysql limit 方法
    sort_type=request.args.get('sort_by')     # 访问接口的url是拼接而成,这里就不指定数据类型
    # sort_type=request.args.get('sort_by',True,type=bool)
    search_date=request.args.get('date')
    if not search_date:   #访问格式有问题  key总是在  并不能总是获取到默认值
        search_date=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    sort_type=True if not sort_type else False  #默认按时间排序 (不传参),传参按统计次数
    if not (user_name and  skip.isdigit() and  off_set.isdigit()):    #判断正整数
        return  jsonify(tip='parameters wrong',log_total_len=0)
    user_search_log=list()
    user_ip_info=models.IPINFO.query.filter_by(logname=user_name).all()
    for each_record in user_ip_info:
        for visit_log in each_record.ip_detail_id:
            if sort_type:
                if str(visit_log.query_time.date()) == search_date:
                    user_search_log.append((visit_log.id,visit_log.partno,visit_log.query_time.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                if str(visit_log.query_time.date()) == search_date:
                    user_search_log.append(visit_log.partno)
    end_index=int(skip)+int(off_set)
    res=list()
    if sort_type:
        search_len=len(user_search_log)
        if int(skip) <  search_len:
            temp_res=sorted(user_search_log,key=lambda  x:x[0],reverse=True)[int(skip):end_index]
            res=[[i[1],i[2]] for i in temp_res if i[1] not  in ['none','nothing'] ] #搜索型号传入有字符串none
    else:
        search_len=len(set(user_search_log))
        if int(skip) < search_len:
            temp_res=sorted(list( set(user_search_log)),key=lambda x :user_search_log.count(x),reverse=True)[int(skip):end_index]
            res=[[i,user_search_log.count(i)] for i in temp_res if i  not in ['none','nothing'] ]
    return jsonify(user=user_name,partno_list=res,log_total_len=search_len,skip_num=int(skip))


@app.route('/test/')
def test_mail():
    """
    测试程序内部错误出发邮件
    :return:
    """
    # msg = Message("Hello",
    #               recipients=["a@qq.com"])
    # msg.body = "testing"
    # msg.html = "<b>testing</b>"
    # mail.send(msg)
    # return  jsonify(ss=1)
    print 'ab%s' %(1,2,3)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """关闭数据库链接"""
    db_session.remove()


def  mail_ipban(method_type,locl_time,ip_list):
    msg=Message('ip_ban_detail',
                recipients=["a@qq.com"])
    msg.body='%s ---------%s----------%s' %(method_type,locl_time,ip_list)
    mail.send(msg)