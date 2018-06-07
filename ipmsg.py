#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,hashlib,requests,datetime


class Webip():
    """
    封装ip信息
    """
    baiduapi = 'http://api.map.baidu.com'
    bdapi_suffix='/location/ip'

    def __init__(self,ip):
        self.ip=ip
        self.value=''

    def url_init(self):
        queryStr = '{api}?ip={ip}&coor=bd09ll&ak={ak}'.format(api=self.bdapi_suffix, ip=self.ip, ak=self.__AK_code)
        encodedStr = urllib.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
        rawStr = encodedStr + self.__SK_code
        md5_value = hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()
        self.url = '{baiduapi}{queryStr}&sn={sn_code}'.format(baiduapi=self.baiduapi, queryStr=queryStr,
                                                              sn_code=md5_value)
        return self.url

    def get_ip_info(self):
        '''
        API 接口使用
        :return:
        '''
        url=self.url_init()
        response=requests.get(url,timeout=5)
        if response.status_code == 200:
            self.value=response.json()
            if self.value['status'] == 0:
                return 0
        return 2001

    def ip_info(self):
        '''
        百度api接口返回ip详细信息
        :return:
        '''
        if self.value:
            city_code=self.value['content']['address_detail']['city_code']
            city=self.value['content']['address']
            temp_info=self.value['address'].split('|')
            country_code=temp_info[0]
            return country_code,city_code,city
        else:
            return ''

    @property
    def md5_ip(self):
        return hashlib.md5(self.ip).hexdigest()












# a=Webip('120.25.64.210')
# # a=Webip('120.77.242.124')
# a=Webip('104.160.41.149')
# print  a.get_ip_info()
# import  json
# print json.dumps(a.get_ip_info(),indent=4,ensure_ascii=False)

