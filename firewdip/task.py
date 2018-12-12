#!/usr/bin/env python
#coding=utf8
from sepcial_edit import *
from config import UseConfig
from  celery import  Celery
from  firewd_ip import  app,mail_ipban
from database import  db_session
from  models import VISIT,IPINFO,IPSEG,AREA
from sqlalchemy import func
import datetime,os,copy,time,json
from aliyun.log.logclient import LogClient
from aliyun.log.getlogsrequest import GetLogsRequest
from ipmsg import Webip
import commands


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
                            VISIT.query_time.between(NOW - datetime.timedelta(minutes=int(excute_time)), NOW)).group_by(
                            VISIT.ip_detail_id).all()
    #timestr分钟查询次数按ip分组，有无用户名都锁住，解锁按制定规则来
    for each in timestr_count_list:
        ip_obj= IPINFO.query.get(each.ip_id)
        rate_time=getattr(ip_obj.ip_area,str_time)
        if each.count_time>rate_time:
            #配置锁定状态，增加锁定次数
            setattr(ip_obj, lock_str, getattr(ip_obj, lock_str) + 1)
            if not (ip_obj.ip_white() or ip_obj.has_logname()):
                ip_obj.lock_status=1
    db_session.commit()


@celery.task()
def unlock_after_lock(count):
    """
    特定规则,下发IP
    """
    too_much_unlock =IPINFO.query.filter(IPINFO.unlock_after_lockd>count,IPINFO.logname=='Anonymous',IPINFO.lock_status==0).all()
    for  each  in too_much_unlock:
        if not each.ip_white():  #如果不是白名单
            each.lock_status=1
            each.lock_1m_times=12345
            each.lock_30m_times=12345
    db_session.commit()


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



'''
日志系统更换
'''

@celery.task()
def icgoo_visit_detail():
    """定期获取ali日志的请求ip,排查直接请求接口的ip 5分钟执行一次"""
    endpoint = ''  # 选择与上面步骤创建Project所属区域匹配的Endpoint
    accessKeyId = ''  # 使用您的阿里云访问密钥AccessKeyId
    accessKey = ''  # 使用您的阿里云访问密钥AccessKeySecret
    project = ''  # 上面步骤创建的项目名称
    logstore = ''  # 上面步骤创建的日志库名称
    client = LogClient(endpoint, accessKeyId, accessKey)
    topic = ""
    To = int(time.time()) + 100
    From1 = To - 500
    From2 = To - 600
    sql1 = "* and request_uri: search/getdata|SELECT   DISTINCT  client_ip limit 0,2000"
    sql2 = "* and request_uri:accounts/is_login |SELECT   DISTINCT  client_ip  limit 0,2000"
    res1 = GetLogsRequest(project, logstore, From1, To, topic, sql1, 2000, 0, False)
    last_res1 = client.get_logs(res1).get_logs()
    time.sleep(50) #扩大白名单搜索时间范围 避免由于请求的间隔过长造成的误封
    res2 = GetLogsRequest(project, logstore, From2, To, topic, sql2, 2000, 0, False)
    last_res2 = client.get_logs(res2).get_logs()
    all_ip = [i.contents['client_ip'] for i in last_res1]
    white_ip = [i.contents['client_ip'] for i in last_res2]
    ip_ban = list(set(all_ip).difference(set(white_ip)))
    # mail_ipban('log',str(To),json.dumps(ip_ban))
    for each_ip in ip_ban:
        #不允许解锁的ip
        ip_str=Webip(each_ip,'Anonymous')
        ip_obj=IPINFO.query.filter(IPINFO.ip_log==ip_str.md5_ip).first()
        if ip_obj:
            if not ip_obj.ip_white():
                (ip_obj.lock_1m_times, ip_obj.lock_30m_times, ip_obj.lock_status,
                 ip_obj.white_list_status, ip_obj.unlock_after_lockd) = sql_results['2']
    db_session.commit()


#异步更新未获取到准确信息的ip
@celery.task()
def up_ip_info():
    import socket
    test_ip=socket.gethostbyname('www.baidu.com')
    baiduapi_is_valid=Webip(test_ip,'test')        #测试api可用性
    if baiduapi_is_valid:
        area_id=AREA.query.filter(AREA.country_code == 'XXX',AREA.city_code == 0).first()
        if area_id:
            ip_obj=IPINFO.query.filter(IPINFO.area_id == area_id.id)
            for each_ip in ip_obj:
                ip_each=Webip(each_ip.ip,each_ip.logname)
                ip_each.get_ip_info()
                country_code,city_code,city=ip_each.ip_info()
                area_id_obj = AREA.query.filter_by(country_code=country_code, city_code=city_code).first()
                if not area_id_obj:
                    area_id_num = AREA(country_code=country_code, city_code=city_code)
                    db_session.add(area_id_num)
                    db_session.commit()
                    ar_id=area_id_num.id
                else:
                    ar_id=area_id_obj.id
                each_ip.area_id=ar_id
                each_ip.area_info=city
                each_ip.lock_status=0 if country_code in white_country_list else 1
            db_session.commit()
    else:
        raise RuntimeError('BaiduAPI  not valid now')


def update_db(status_code):
    '''替换ip_list 批量更新ip'''
    ip_list = []
    for each_ip in ip_list:
        #自定义批量处理ip
        ip_str = Webip(each_ip, 'Anonymous')
        ip_obj = IPINFO.query.filter(IPINFO.ip_log == ip_str.md5_ip).first()
        if ip_obj:
            if not ip_obj.ip_white():
                (ip_obj.lock_1m_times, ip_obj.lock_30m_times, ip_obj.lock_status,
                 ip_obj.white_list_status, ip_obj.unlock_after_lockd) = sql_results[status_code]
    db_session.commit()


def produce_ip_file(mode):
    """
    每三分钟下发最新IP，如果文件没发生改变就无操作
    ali日志系统使得源ip改变，所以关闭定时任务

    :return:
    """
    all_info =db_session.query(IPINFO.ip).filter(IPINFO.logname != 'Anonymous').group_by(IPINFO.ip).all()
    all_seg = IPSEG.query.filter(IPSEG.ipseg_status == 1).all()
    ip_drop = '<?xml version="1.0" encoding="utf-8"?>\n<ipset type="hash:net">\n<entry>0.0.0.0/0</entry>\n</ipset>'
    ip_white = '<?xml version="1.0" encoding="utf-8"?>\n<ipset type="hash:net">'
    for each in all_info:
        str_ip = '\n<entry>%s</entry>' % each[0]
        ip_white += str_ip
    ip_white += '\n</ipset>'
    # for each_seg in all_seg:
    #     str_ip = '\n<entry>%s</entry>' % (each_seg.ip+'.1/24')
    #     ip_white += str_ip
    # ip_white += '\n</ipset>'
    if not os.path.exists(path_file_drop):
        os.mknod(path_file_drop)
    if not os.path.exists(path_file_white):
        os.mknod(path_file_white)
    path_drop_new = os.path.join(base_dir, ('temp_%s' % dropfile_name))
    path_white_new = os.path.join(base_dir, ('temp_%s' % rdtfile_name))
    with open(path_drop_new, 'w+') as f, open(path_white_new, 'w') as g:
        f.write(ip_drop)
        g.write(ip_white)
    cmd_str1 = 'diff %s %s |wc -l ' % (path_file_drop, path_drop_new)
    cmd_str2 = 'diff %s %s |wc -l' % (path_file_redirect, path_white_new)
    drop_status = os.popen(cmd_str1).read().strip()
    white_status = os.popen(cmd_str2).read().strip()
    if int(drop_status) != 0 or int(white_status) != 0:
        os.unlink(path_file_drop)
        os.unlink(path_file_white)
        os.rename(path_drop_new, path_file_drop)
        os.rename(path_white_new, path_file_white)
    #暂且保存文件对比功能
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fwd_ctr='fab upfwp_ip:{}'.format(mode)
    commands.getstatusoutput(fwd_ctr)
















