from flask import Flask
from flask.ext import flask_restful
from flask.ext.mail import Mail
from flask_sqlalchemy import  SQLAlchemy
app = Flask(__name__)
app.config['DEBUG']=True



#sql 配置
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:171024@127.0.0.1/ipfire'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)




#邮件配置
app.config.update(
    DEBUG = True,
    MAIL_SERVER='smtp.sina.com',
    MAIL_PROT=25,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'test_code@sina.com',
    MAIL_PASSWORD = 'pwd@test',
    MAIL_DEBUG = True
)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
