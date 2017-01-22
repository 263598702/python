#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-11-25 11:28:36
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import urllib
import urllib2
import re
import codecs

class BDTB:
    def __init__(self,baseUrl,seeLz,floorTag):
        self.baseUrl=baseUrl
        self.seeLz='?see_lz='+str(seeLz)
        self.tool=Tool()
        self.file=None
        self.floor=1
        self.defaultTitle=u'百度贴吧'
        self.floorTag=floorTag

    def getPage(self,pageNum):
        try:
            url=self.baseUrl+self.seeLz+'&pn='+str(pageNum) 
            request=urllib2.Request(url)
            response=urllib2.urlopen(request) 
            return response.read().decode('utf-8')
        except urllib2.URLError,e:
            print u'连接百度贴吧失败，错误原因', e.reason
            return None

    def getTitle(self,page): 
        pattern=re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
        result=re.search(pattern,page)
        if(result):
            return result.group(1).strip()
        else:
            return None

    def getPageTotal(self,page): 
        parttern=re.compile('<li class="l_reply_num.*?</span>.*?<span class="red">(.*?)</span>',re.S)
        result=re.search(parttern,page)
        if(result):
            return result.group(1).strip()
        else:
            return None

    def getContent(self,page):
        pattern=re.compile('<div id="post_content_.*?>(.*?)</div><br>',re.S)
        items=re.findall(pattern,page)
        contents=[]
        for item in items:
            content='\n'+self.tool.replace(item)+'\n'
            contents.append(content)
        return contents

    def writeData(self,contents):
        for item in contents:
            if self.floorTag=='1':
                floorLine='\n'+str(self.floor)+u'------------------------------------------------------------------------------\n'
                self.file.write(floorLine)
            self.file.write(item)
            self.floor+=1

    def setFileTitle(self,title):
        if title is not None:
            self.file=codecs.open('NBA.txt','a','utf-8') 
        else:
            self.file=codecs.open('NBA.txt','a','utf-8')

    def start(self):
        indexPage=self.getPage(1)
        pageNum=self.getPageTotal(indexPage)
        title=self.getTitle(indexPage)
        self.setFileTitle(title)
        if pageNum==None:
            print 'URL已失效，请重试'
            return
        try: 
            print u"该帖子共有" + str(pageNum) + u"页"
            for i in range(1,int(pageNum)+1): 
                print u'正在写入第'+str(i)+u'页数据'
                page=self.getPage(i)
                contents=self.getContent(page)
                self.writeData(contents)
        except IOError,e:
            print u'写入异常，原因：'+e.Message
        finally:
            print u'写入完成'



class Tool:
    removeImg=re.compile('<img.*?>| {7}|')
    removeAddr=re.compile('<a.*?>|</a>')
    replaceLine=re.compile('<tr>|<div>|</div>|</p>')
    replaceTd=re.compile('<td>')
    replacePara=re.compile('<p.*?>')
    replaceBr=re.compile('<br><br>|<br>')
    removeExtraTag=re.compile('<.*?>')

    def replace(self,x):
        x = re.sub(self.removeImg,'',x)
        x = re.sub(self.removeAddr,'',x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTd,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBr,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)

        return x.strip()


baseUrl='http://tieba.baidu.com/p/3138733512'
bdtb=BDTB(baseUrl,1,'1') 
bdtb.start()
 


