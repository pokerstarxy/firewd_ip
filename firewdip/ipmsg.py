#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,hashlib,requests,os,re
import geoip2.database
from geoip2.errors import  AddressNotFoundError
from requests.adapters import HTTPAdapter


class Webip():
    """
    封装ip信息
    """
    __AK_code = 'tt'
    __SK_code = 'vv'
    baiduapi = 'http://api.map.baidu.com'
    bdapi_suffix='/location/ip'
    basedir = os.path.dirname(os.path.abspath(__file__))
    pattern = re.compile(r'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)')

    def __init__(self,ip,logname):
        self.ip=ip
        self.value=''
        self.logname=logname

    def  ip_valid(self):
        """验证ip有效性"""
        return re.match(self.pattern,self.ip)

    def getip_country_code(self):
        path=os.path.join(self.basedir,'geoipdb/GeoLite2-Country.mmdb')
        reader = geoip2.database.Reader(path)
        try:
            data=reader.country(self.ip)
        except  AddressNotFoundError:
            return 'local',0,'ali'
        try:
            CountryName=data.country.names['zh-CN']
        except Exception as e:
            # print e
            CountryName=data.country.name
        return data.country.iso_code,0,CountryName

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
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=1))
        s.mount('https://', HTTPAdapter(max_retries=1))
        try:
            response=s.get(url,timeout=2)
        except requests.ConnectionError:                             #baiduapi 链接超时 则构造数据返回
            self.value={
                'address':'XXX|Mars',
                'status':0,
                'content':{
                    'address':u'火星',
                    'address_detail':{
                                                             'city_code':0
                                                            },
                                        }
                                    }
        else:
            if response.status_code == 200:
                self.value = response.json()
                return 1    #api 正常返回1
            else:
                raise RuntimeError('BaiDu API Error  --%s--%s'.format(response.status_code,response.text))

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
        return hashlib.md5(self.ip+self.logname).hexdigest()


