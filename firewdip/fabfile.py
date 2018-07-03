# coding=utf-8
from fabric.api import *
from fabric.context_managers import *
from sepcial_edit import  path_file_drop,path_file_redirect

env.password = "aaaaa"

# icgoo-webs on aliyun
ig_ips = ["root@ig%s.xxx.cn" %i  for i in range(2,31)]
# ig_ips = ["root@ig%s.k0v.cn" %i  for i in range(10,11)]

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
fwd_set_black="firewall-cmd --zone=public --{method}-rich-rule='rule source ipset={listname} {operate}'"
fwd_set_white="firewall-cmd  --zone=public --{method}-rich-rule='rule family=ipv4  source ipset={listname}  forward-port port=443 to-port=80 protocol=tcp '"
add_port=' firewall-cmd --permanent --zone=public --add-port={port}/tcp'
cmd_str3=fwd_set_black.format(method='add',listname='blacklist',operate='drop')
cmd_str4=fwd_set_black.format(method='remove',listname='blacklist',operate='drop')
cmd_str5=fwd_set_white.format(method='add',listname='whitelist')
cmd_str6=fwd_set_white.format(method='remove',listname='whitelist')


@task
@parallel
def init_firewalld():
    """
    ali防火墙有配置,不好完全初始化，基于我的功能进行初始化

    :return:

    """
    run('yum install ipset -y ')
    run('service firewalld restart')
    port_str1=add_port.format(port='8088')
    port_str2=add_port.format(port='443')
    port_str3=add_port.format(port='6042')
    run(port_str1)
    run(port_str2)
    run(port_str3)
    run(command.format(operate='new',listname='blacklist'))   #delete
    run(command.format(operate='new',listname='whitelist'))
    run('chkconfig firewalld off')            #重启机器后记得开启防火墙服务





@task
@parallel
def   upfwp_ip():
    """
    重载配置,获取最新封禁ip
    :return:
    """
    run('service firewalld restart')
    put(path_file_drop,'/etc/firewalld/ipsets/blacklist.xml')
    put(path_file_redirect,'/etc/firewalld/ipsets/whitelist.xml')
    run('firewall-cmd --add-masquerade')    #添加转发
    run(cmd_str3)
    run(cmd_str5)




@task
@parallel
def  reset_fwd():
    """
    重置定制防火墙功能(针对封禁爬虫的重置);除去本身的ali功能和必要的端口开放(已添加至配置文件)
    :return:
    """

    run('service firewalld restart')
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
@parallel
def get_ip():
    '''
    查询调用了search接口却没有使用login接口的ip
    :return:
    '''
    a=run("cat /var/log/nginx-icgoo-access.log |awk '{print $1,$7}'|grep /accounts/is_login|sort  |uniq -c|sort -rn|awk '{print $2}'")
    d= a.split('\r\n')
    print 'valid--',
    print d
    b=run("cat /var/log/nginx-icgoo-access.log |grep '/search/' |awk '{print $1,$7}'|sort  |uniq -c|sort -rn|awk '{print $2}'")
    c=b.split('\r\n')
    print 'allip--',
    print c

"""
firewall-cmd  --ipset=blacklist --add-entry=192.168.8.96     --remove  直接生效

"""
