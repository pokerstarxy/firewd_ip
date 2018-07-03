#!/usr/bin/env python
#coding=utf8
from sepcial_edit import *
from config import UseConfig
from  celery import  Celery
from  firewd_ip import  app
from database import  db_session
from  models import VISIT,IPINFO,IPSEG
from sqlalchemy import func
import datetime,os,copy
from ipmsg import Webip


def make_celery(app):
    celery = Celery(
    app.import_name,
    broker=UseConfig.CELERY_BROKER_URL,
    backend=UseConfig.CELERY_RESULT_BACKEND
    )
    celery.conf.update(app.config)
    Taskbase=celery.Task
    class ContextTask(Taskbase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return Taskbase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@celery.task()
def my_task():
    print 'test celery'


@celery.task()
def ip_limit_rate():
    '''
    每分钟只有一个任务
    1小时执行60个任务
    ---正常规则---
    有无用户名都会被锁
    无用户名不可多次解锁
    黑白名单   ip段只可以手工在后台添加,定时任务最多添加不让解锁    因误伤太严重
    :return:
    '''
    minute_value=datetime.datetime.now().minute
    excute_time_copy=copy.deepcopy(excute_time_list)
    while True:
        excute_time=excute_time_copy.pop()
        if not minute_value%excute_time:
            break
    str_time='rate_{}m'.format(str(excute_time))
    lock_str='lock_{}m_times'.format(str(excute_time))
    NOW=datetime.datetime.now()
    timestr_count_list=db_session.query(VISIT.ip_detail_id.label('ip_id'),
                                        func.count(VISIT.ip_detail_id).label('count_time')).filter(
                            VISIT.query_time.between(NOW - datetime.timedelta(minutes=5), NOW)).group_by(
                            VISIT.ip_detail_id).all()
    #timestr分钟查询次数按ip分组，有无用户名都锁住，解锁按制定规则来
    for each in timestr_count_list:
        ip_obj= IPINFO.query.get(each.ip_id)
        rate_time=getattr(ip_obj.ip_area,str_time)
        if each.count_time>rate_time:
            #配置锁定状态，增加锁定次数
            setattr(ip_obj, lock_str, getattr(ip_obj, lock_str) + 1)
            if not ip_obj.ip_white():
                ip_obj.lock_status=1
    db_session.commit()


@celery.task()
def unlock_after_lock(count):
    """
    特定规则,下发IP
    """
    too_much_unlock =IPINFO.query.filter(IPINFO.unlock_after_lockd>count,IPINFO.logname=='Anonymous').all()
    for  each  in too_much_unlock:
        if not each.ip_white():  #如果不是白名单
            each.lock_status=1
            each.lock_1m_times=12345
            each.lock_30m_times=12345
    db_session.commit()


@celery.task()
def produce_ip_file():
    """
    每三分钟下发最新IP，如果文件没发生改变就无操作
    :return:
    """
    all_info=IPINFO.query.filter(IPINFO.white_list_status=='9').all()
    all_seg=IPSEG.query.filter(IPSEG.ipseg_status==1).all()
    ip_drop = '<?xml version="1.0" encoding="utf-8"?>\n<ipset type="hash:net">'
    ip_redirect = '<?xml version="1.0" encoding="utf-8"?>\n<ipset type="hash:net">'
    for each in all_info:
            str_ip = '\n<entry>%s</entry>' % each.ip
            ip_drop += str_ip
    for each_seg in all_seg:
        str_ip = '\n<entry>%s</entry>' % (each_seg.ip+'.1/24')
        ip_redirect += str_ip
    ip_redirect += '\n</ipset>'
    if not os.path.exists(path_file_drop):
        os.mknod(path_file_drop)
    if not os.path.exists(path_file_redirect):
        os.mknod(path_file_redirect)
    path_drop_new = os.path.join(base_dir, ('temp_%s' % dropfile_name))
    path_redirect_new = os.path.join(base_dir, ('temp_%s' % rdtfile_name))
    with open(path_drop_new, 'w+') as f, open(path_redirect_new, 'w') as g:
        f.write(ip_drop)
        g.write(ip_redirect)
    cmd_str1 = 'diff %s %s |wc -l ' % (path_file_drop, path_drop_new)
    cmd_str2 = 'diff %s %s |wc -l' % (path_file_redirect, path_redirect_new)
    drop_status = os.popen(cmd_str1).read().strip()
    redirct_status = os.popen(cmd_str2).read().strip()
    if int(drop_status) != 0 or int(redirct_status) != 0:
        os.unlink(path_file_drop)
        os.unlink(path_file_redirect)
        os.rename(path_drop_new, path_file_drop)
        os.rename(path_redirect_new, path_file_redirect)


@celery.task()
def init_today_search_times():
    IPINFO.query.filter().update({'today_times':0})
    db_session.commit()


@celery.task()
def update_geoip_database():
    """
    安装weget
    :return:
    """
    basedir = os.path.dirname(os.path.abspath(__file__))
    basicdir=os.path.dirname(basedir)
    path = os.path.join(basedir, 'aa.tar.gz')
    url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz'
    str_cmd = 'wget   -t5  -qc  -T 10  %s  -O %s' % (url, path)
    unzip_file_cmd = 'tar -zxvf  %s ' % (path)
    delete_file="find  %s   -type d  -name 'GeoLite2*' |xargs  rm -rf " %basicdir
    move_cmd = "find %s   -maxdepth 2 -type f  -name   'GeoLite2-Country*'   -exec mv  -f  {}  %s \;" % (
        basicdir, os.path.join(basedir, 'geoipdb'))
    os.system(str_cmd)
    os.system(unzip_file_cmd)
    os.unlink(path)
    os.system(move_cmd)
    os.system(delete_file)



@celery.task()
def icgoo_visit_detail():
    """定期获取nginx日志的请求ip"""
    ip_normal=list()
    ip_all=list()
    os.chdir(base_dir)
    os.system('fab  get_ip --hide stdout,running  > ip_nginx.txt')
    os.system("sed -i '$d' ip_nginx.txt")
    with open('ip_nginx.txt','r') as f:
        for each in f.readlines():
            temp_line=each.strip().split('--')
            if temp_line[0] == 'visit':
                ip_normal.extend(eval(temp_line[1].strip()))
            elif  temp_line[0] == 'allip':
                ip_all.extend(eval(temp_line[1].strip()))
    ip_ban=set(ip_all)-set(ip_normal)
    for each_ip in ip_ban:
        #白名单不准这样查 --这里不判断白名单 ,直接封流量
        ip_str=Webip(each_ip,'Anonymous')
        ip_obj=IPINFO.query.filter(IPINFO.ip_log==ip_str.md5_ip).first()
        (ip_obj.lock_1m_times, ip_obj.lock_30m_times, ip_obj.lock_status,
         ip_obj.white_list_status, unlock_after_lockd) = sql_results['3']
    db_session.commit()



















