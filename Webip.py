#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib,hashlib,requests

"""
状态码：
0      正常返回
1      无法获取到百度API的返回值

"""


class Webip():
    """
    封装ip信息
    """
    baiduapi = 'http://api.map.baidu.com'
    bdapi_suffix='/location/ip'

    def __init__(self,ip):
        self.ip=ip

    def url_init(self):
        queryStr = '{api}?ip={ip}&coor=bd09ll&ak={ak}'.format(api=self.bdapi_suffix, ip=self.ip, ak=self.__AK_code)
        encodedStr = urllib.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
        rawStr = encodedStr + self.__SK_code
        md5_value = hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()
        self.url = '{baiduapi}{queryStr}&sn={sn_code}'.format(baiduapi=self.baiduapi, queryStr=queryStr,
                                                              sn_code=md5_value)
        return self.url

    def get_ip_info(self):
        url=self.url_init()
        response=requests.get(url,timeout=5)
        if response.status_code == 200:
            self.value=response.json()
            if self.value['status'] == 0:
                return self.value,0
        return 'WebIp',1










a=Webip('120.25.64.210')
import  json
print json.dumps(a.get_ip_info(),indent=4,ensure_ascii=False)

