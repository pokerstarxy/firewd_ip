#!/usr/bin/env python
#coding=utf8
from wtforms import Form,StringField,validators,SubmitField,SelectField


class  IpInfoForm(Form):
    ip=StringField('IpAddr', validators=[validators.IPAddress(),validators.DataRequired()])
    choice = SelectField('Choice', choices=[
        ('0', 'Unblock and set to whitelist'),
        ('1', 'Unblock IP'),
        ('2', ' Block IP'),
        ('3', 'Black Ip'),
        ('4', 'Block IP Seg '),
        ('5', 'Unblock IP Seg '),
    ])
    submit = SubmitField('submit')