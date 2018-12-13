# markdown   test
                   
    
## 限制访问频率

### 主要结构
1.  geoipdb  分析国外ip的国家编码 --定期更新
2.  fab file 主要做一些后端的批量操作
3.  homepage 后台文件，提供ip状态修改的界面
4.  ipmsg ip信息接口  国内用的百度api 国外用的geoip
5.  sepcial_edit  部分可修改参数
6.  task 异步任务
7.  database 数据库接口文件  可以用于测试时候创建删除数据库
8. supervisor+nginx+gunicorn
9. update test