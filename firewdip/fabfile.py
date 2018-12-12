# coding=utf-8
from fabric.api import *
from fabric.context_managers import *
from sepcial_edit import  path_file_drop,path_file_redirect,path_file_white

env.password = "pwd"

ig_ips = ["root@%s.test.cn" %i  for i in range(2,31)]

env.hosts  = ig_ips

"""
method       add remove  添加删除规则   以下命令未修改配置文件
num    优先级      --维护两个列表 redirect +  drop
ipsetlist     自定义的ipset的名字
operate       DROP  REDIRECT 防火墙操作
extra        额外配置
"""
#命令检测,生成相应文件
command='firewall-cmd --permanent --{operate}-ipset={listname} --type=hash:net'
fwd_set="firewall-cmd --zone=public --{method}-rich-rule='rule source ipset={listname} {operate}'"
fwd_set_redirect="firewall-cmd  --zone=public --{method}-rich-rule='rule family=ipv4  source ipset={listname}  forward-port port=443 to-port=80 protocol=tcp '"
cmd_port=' firewall-cmd --permanent --zone=public --{operate}-port={port}/tcp'
#防火墙测试优先级    以免完全屏蔽
cmd_str3=fwd_set.format(method='add',listname='blacklist',operate='drop')
cmd_str4=fwd_set.format(method='remove',listname='blacklist',operate='drop')
cmd_str5=fwd_set_redirect.format(method='add',listname='redirectlist')
cmd_str6=fwd_set_redirect.format(method='remove',listname='redirectlist')
cmd_str7=fwd_set.format(method='add',listname='whitelist',operate='accept')
cmd_str8=fwd_set.format(method='remove',listname='whitelist',operate='accept')



@task
@parallel
def init_firewalld():
    """
    ali防火墙有配置,不好完全初始化，基于我的功能进行初始化

    :return:

    """
    run('yum install ipset -y ')
    run('service firewalld restart')
    port_str1=cmd_port.format(operate='add',port='8088')
    port_str2=cmd_port.format(operate='add',port='443')
    port_str3=cmd_port.format(operate='add',port='6042')
    run(port_str1)
    run(port_str2)
    run(port_str3)
    run(command.format(operate='new',listname='blacklist'))   #delete
    run(command.format(operate='new',listname='redirectlist'))   #redirect
    run(command.format(operate='new',listname='whitelist'))  #accept
    run('chkconfig firewalld off')            #重启机器后记得开启防火墙服务





@task
@parallel
def   upfwp_ip(operate_port):
    """
    重载配置,获取最新封禁ip
    :return:
    """
    if operate_port == 'open':
        port_str1 = cmd_port.format(operate='add', port='8088')
        port_str2 = cmd_port.format(operate='add', port='443')
    elif operate_port == 'close':
        port_str1 = cmd_port.format(operate='remove', port='8088')
        port_str2 = cmd_port.format(operate='remove', port='443')
        put(path_file_white, '/etc/firewalld/ipsets/whitelist.xml')
    else:
        print 'Parameter error'
        return
    run(port_str1)
    run(port_str2)
    run(' firewall-cmd --reload')
    run(cmd_str7)
    # put(path_file_drop,'/etc/firewalld/ipsets/blacklist.xml')
    # put(path_file_white,'/etc/firewalld/ipsets/whitelist.xml')
    # put(path_file_redirect,'/etc/firewalld/ipsets/redirectlist.xml')
    # run('firewall-cmd --add-masquerade')    #添加转发
    # run(cmd_str3)
    # run(cmd_str5)





@task
@parallel
def  reset_fwd():
    """
    重置定制防火墙功能(针对封禁爬虫的重置);除去本身的ali功能和必要的端口开放(已添加至配置文件)
    :return:
    """

    run('service firewalld restart')
    # run("ipset list|grep Name |awk -F ':' '{print $2}' |xargs -l ipset destroy") #清空ipset集合
    #初始化之前的问题



@task
@parallel
def   init_web():
    """
    80端口为开放的nginx自带的服务，重定向到80

    下发nginx 文件
    只对443端口 redirect
    :return:
    """
    filename=''
    put(filename,'/usr/share/nginx/html')



@task
def get_ip():
    '''
    查询调用了search接口却没有使用login接口的ip
    :return:
    '''
    a=run("cat /var/log/nginx-access.log|awk '{print $1,$7}'|grep /accounts/is_login|awk '{print $1}'|sort  |uniq -c|sort -rn|awk '{print $2}'")
    d= a.split('\r\n')
    print 'visit--%s' %str(d)
    b=run("cat /var/log/nginx-access.log|awk '{print $1,$7}' |grep '/search/' |awk '{print $1}'|sort  |uniq -c|sort -rn |awk '{print $2}'")
    c=b.split('\r\n')
    print 'allip--%s' %str(c)

"""
firewall-cmd  --ipset=blacklist --add-entry=192.168.8.96     --remove  直接生效

"""
