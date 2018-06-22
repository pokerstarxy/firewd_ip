#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,hashlib,requests,os
import geoip2.database


class Webip():
    """
    封装ip信息
    """
    baiduapi = 'http://api.map.baidu.com'
    bdapi_suffix='/location/ip'
    basedir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self,ip):
        self.ip=ip
        self.value=''

    def getip_country_code(self):
        path=os.path.join(self.basedir,'geoipdb/GeoLite2-Country.mmdb')
        reader = geoip2.database.Reader(path)
        data=reader.country(self.ip)
        return data.country.iso_code,0,data.country.names['zh-CN']

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
        API 接口使用  是否正常
        :return:
        '''
        url=self.url_init()
        response=requests.get(url,timeout=5)
        if response.status_code == 200:
            self.value = response.json()
            return 0
        else:
            return  1

    def ip_info(self):
        '''
        百度api接口返回ip详细信息
        国外ip 特殊处理,仅仅返回国家编码
        :return:
        '''
        if self.value['status'] == 0:
            city_code = self.value['content']['address_detail']['city_code']
            city = self.value['content']['address']
            temp_info = self.value['address'].split('|')
            country_code = temp_info[0]
            return country_code, city_code, city
        else:
            # 国外IP 仅仅针对国家编码处理
            return self.getip_country_code()

    @property
    def md5_ip(self):
        return hashlib.md5(self.ip).hexdigest()


