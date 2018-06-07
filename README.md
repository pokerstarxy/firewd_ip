# firewd_ip
ip ban
fwd_ip


1    数据库    mysql

   1) 表结构



2   接口

    1) restapi 原则


3   内存数据库

        1）数据存储



4  防火墙配置

    如何下发？



5   策略
    ip 频率









  ip 表       查询记录
  id,partno,query_time,foriegn_key_ipinfo


  ip 状态    ip信息

  id,ip,logname,md5(ip+logname),lock_status,unlock_times,1m,10m,60m,total_times,today_times,key_country_code,key_city_code,create_time,lastest_time,ipseg_status,white_list_status(0,1,2)


  次数限值     限制次数    计数式限制
                                --限制区域
                 --海外
login                      --非限制区域
                                    --限制省份
                   --国内
                                    --非限制省份

               --限制区域
                 --海外
notlogin                      --非限制区域
                                    --限制省份
                   --国内
                                    --非限制省份




  区域         地区
  id     country_code     area_code     inCN









ip段怎么设置
ip 信息直接给出？    --定义规则 添加记录？

id   ipseg(md5)   status  create_time








接口格式
ip信息封装(接口选择)
定时任务
循环调用
机器学习？限制非登录用户接口访问次数
celery 任务
清cache 任务    固定配置
异步任务定时 获取 配置信息   主动和被动