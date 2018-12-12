#!/usr/bin/env python
#coding=utf8
from flask_admin import  BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask import  request,flash,Response
from models import IPSEG,IPINFO
from database import  db_session
from form import IpInfoForm
from sepcial_edit import  sql_results
import hashlib
from werkzeug.exceptions import HTTPException


class ModelView(ModelView):
    def is_accessible(self):
        from firewd_ip import app
        auth = request.authorization or request.environ.get('REMOTE_USER')  # workaround for Apache
        if not auth or (auth.username, auth.password) != app.config['ADMIN_CREDENTIALS']:
            raise HTTPException('', Response(
                "Please log in.", 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            ))
        return True


class MyView(BaseView):
    @staticmethod
    def ip_md5(ip_addr):
        return hashlib.md5(ip_addr).hexdigest()

    @expose('/',methods=('GET', 'POST'))
    def index(self):
        if   request.method=='GET':
            form = IpInfoForm()
            message="""
            please input ip and  choice:
            """
            return self.render('myIndex.html',message=message,form=form)
        else:
            ip=request.form['ip']
            para_tp=request.form['choice']
            form = IpInfoForm(request.form)
            if   form.validate() and   para_tp in sql_results.keys():
                if  int(para_tp)<4:
                    md5_ip =self.ip_md5(ip+'Anonymous')
                    ip_obj=IPINFO.query.filter_by(ip_log=md5_ip).first()
                    if  ip_obj:
                        #这里不存在就不去添加了 --人为改，不判断是否白名单
                        ip_obj.unlock_times+=1
                        (ip_obj.lock_1m_times,ip_obj.lock_30m_times,ip_obj.lock_status,
                        ip_obj.white_list_status,unlock_after_lockd)=sql_results[para_tp]
                else:
                    #封ip段不管有没有用户名
                    ipseg_list=ip.split('.')
                    ipseg_list.pop()
                    ip_str='.'.join(ipseg_list)
                    md5_ip=self.ip_md5(ip_str)
                    ip_obj=IPSEG.query.filter_by(ipseg=md5_ip).first()
                    if  not ip_obj:
                        ip_obj=IPSEG(ip_str,md5_ip)
                        db_session.add(ip_obj)
                        db_session.commit()
                    ip_obj.ipseg_status=sql_results[para_tp]
                db_session.commit()
                message='ip  %s changed to status %s' %(ip,para_tp)
                flash('update success')
                return  self.render('myIndex.html',message=message,form=form)
            else:
                flash('ip or choice wrong')
                message = 'please try again'
                return self.render('myIndex.html', message=message, form=form)


class IPModelView(ModelView):
    page_size = 50
    can_view_details = True
    can_create = False
    can_edit = False
    can_delete = False
    column_exclude_list = ['ip_log', 'create_time','lastest_time','ipseg']
    column_searchable_list = ['ip']


class  IpAreaView(ModelView):
    page_size = 50
    can_view_details = True
    can_create = False
    can_delete = False
    can_edit = False
    column_editable_list = [
        'rate_1m', 'rate_30m',
        'rate_ipseg_30m',
        'lock_max_1m',
        'lock_max_30m']
    column_searchable_list = ['city_code']


class IpSegModelView(ModelView):
    page_size = 50
    can_view_details = True
    can_create = False
    can_delete = False
    can_edit = False
    column_editable_list=['ipseg_status',]
    column_exclude_list = ['create_time','ipseg']
    column_searchable_list = ['ip']
    form_choices={
        'ipseg_status':[
            ('0','0'),
            ('1','1'),
        ]
    }


