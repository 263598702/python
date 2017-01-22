# -*- coding: UTF-8 -*-

import re
import urllib2
import urllib

from collections import deque

queue=deque()

visited=set()
url='http://www.cnblogs.com'
queue.append(url)
cnt=0
while queue:
    url=queue.popleft()
    visited |={url}
    print('已经抓取: ' + str(cnt) + ' 正在抓取 <--- ' + url) 
    cnt+=1
    user_agents = [  
                   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'
                   ]   
    headers={ 
    'User-Agent': user_agents} 
    req = urllib2.Request(url,headers=headers)   
    try:
        urlop=urllib2.urlopen(req) 
    except Exception as e:
        print urlop.read

    try:
         data=urlop.read() 
    except:
         continue

    linkre=re.compile("href=['\"]([^\"'>]*?)['\"].*?")
    for x in linkre.findall(data):
        if 'http' in x and x not in visited:
            queue.append(x)
            print('加入队列 ---->' + x)