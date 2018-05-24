import logging
from flask import Flask
from flask.ext import flask_restful
from flask.ext.mail import Mail,Message
from logging.handlers import SMTPHandler
from flask.ext.cache import Cache
from logging import getLogger
from logging import Formatter
app = Flask(__name__)
# app.config.update(
#     DEBUG=True,
#     MAIL_SERVER='smtp.sina.com',
#     MAIL_PROT=25,
#     MAIL_USE_TLS = True,
#     MAIL_USE_SSL = False,
#     MAIL_USERNAME = 'test_code@sina.com',
#     MAIL_PASSWORD = 'pwd@test',
#     MAIL_DEBUG = True
# )
#
# config = {
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_HOST': '127.0.0.1',
#     'CACHE_REDIS_PORT': 6379,
#     'CACHE_REDIS_DB': '',
#     'CACHE_REDIS_PASSWORD': ''
# }
# app.config.from_object(config)
# cache.init_app(app)
# ADMINS = ['yourname@example.com']
# if not app.debug:
#     mail_handler = SMTPHandler('127.0.0.1',
#                                'server-error@example.com',
#                                ADMINS, 'YourApplication Failed')
#     mail_handler.setLevel(logging.ERROR)
#     mail_handler.setFormatter(Formatter('''
#     Message type:       %(levelname)s
#     Location:           %(pathname)s:%(lineno)d
#     Module:             %(module)s
#     Function:           %(funcName)s
#     Time:               %(asctime)s
#
#     Message:
#
#     %(message)s
#     '''))
#     app.logger.addHandler(mail_handler)
#     loggers = [app.logger, getLogger('sqlalchemy'),
#                getLogger('mail')]
#     for logger in loggers:
#         logger.addHandler(mail_handler)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
