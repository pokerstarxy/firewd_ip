#!/usr/bin/env python
#coding=utf8
from flask_script import Manager
from database import Base
from flask_migrate import Migrate, MigrateCommand
from firewdip.firewd_ip import  app

migrate = Migrate(app,Base)
manager = Manager(app)
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    """compare_type = True, 配置env 跟踪表字段修改
            表结构修改请运行
                                python manage.py db migrate
                                python manage.py db upgrade
             重命名需要使用alembic语法，不然数据会丢失
    """
    manager.run()
