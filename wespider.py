#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-03 10:30:02
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import urllib
import urllib2

#两种请求方式结果相同 
#request=urllib2.Request('http://www.ttce.cn')
#response=urllib2.urlopen(request)
#response=urllib2.urlopen('http://www.ttce.cn')
#html=response.read()
#print html
 
'''
values={
	'Gid':57995,
	'Uid':864291,
	'Number':2,
	'ShopId':864291,
	'SpeValueId':311152
}

url_values=urllib.urlencode(values)
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor)
request=urllib2.Request('http://buy.test.com/api/Cart/PostAddCart')
response=opener.open(request,url_values) 
print response.read()
''' 
'''
req=urllib2.Request('http://bbs.csdn.net/callmewhy')

try:
	urllib2.urlopen(req)
	print 1
except urllib2.URLError,e:
	print e.code
'''
'''
from urllib2 import Request,urlopen,URLError,HTTPError

req=urllib2.Request('http://www.csdn.net/callmewhy')

try:
	response=urlopen(req)
except URLError,e:
	print e.reason
	if hasattr(e,'code'):
		print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
	elif hasattr(e,'reason'):
		print 'We failed to reach a server.'
		print 'Reason: ', e.reason
else:
	print 'No Exception was raised.'
    '''
'''
import cookielib

filename='cookie.txt'
cookie=cookielib.MozillaCookieJar(filename)
handler=urllib2.HTTPCookieProcessor(cookie)
opener=urllib2.build_opener(handler)
response=opener.open('http://www.baidu.com')
for item in cookie:
    print item.name+':'+item.value 

cookie.save(ignore_discard=True,ignore_expires=True)
'''
'''
import cookielib

cookie=cookielib.MozillaCookieJar()
cookie.load('cookie.txt',ignore_discard=True,ignore_expires=True)
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
req=urllib2.Request('http://www.baidu.com')
response=opener.open(req)
print response.read()
'''

#模拟登录so.ttce.cn
import cookielib

'''
filename='jhcookie.txt'
cookie=cookielib.MozillaCookieJar(filename)
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
values={
    'txtUserName':'zzjttce',
    'txtPassWord':'zzjttce',
    'txtValidateCode:':'',
    'txtValidateSid:':'',
    'url':''
}
url_values=urllib.urlencode(values)
req=urllib2.Request('http://so.ttce.cn/login/UserLogin')
response=opener.open(req,url_values)
cookie.save(ignore_discard=True,ignore_expires=True)
print response.read()

'''

cookie=cookielib.MozillaCookieJar() 
cookie.load('jhcookie.txt',ignore_discard=True,ignore_expires=True)
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
req=urllib2.Request('http://buy.ttce.cn')
response=opener.open(req)
print response.read()
