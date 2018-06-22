#!/usr/bin/env python
#coding=utf8
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from firewdip.firewd_ip import app,db_session
from firewdip.models  import *

manager = Manager(app)

migrate = Migrate(app, db_session)

manager.add_command('db_session', MigrateCommand)


if __name__ == '__main__':
    manager.run()