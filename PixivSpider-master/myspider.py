import os
import time
from os import sys
import urllib.request
import http.cookiejar
import threading
import re
import json
from bs4 import BeautifulSoup 
from queue import Queue

def getTime(intVal):
    h=0
    m=0
    s=intVal
    if(s>60):
        m=s//60
        s-=m*60
    if(m>60):
        h=m//60
        m-=h*60
    return format("%02d h %02d m %02d s" %(h,m,s))

class downloader(threading.Thread):
    def __init__(self,q,path,opener):
        threading.Thread.__init__(self)
        self.q=q
        self.filename=""
        self.sch=0
        self.path=path
        self.opener=opener 
        self.is_working=False
        self.exitflag=False

    def run(self):
        def report(blocks,blocksize,total):
            self.sch=int(blocks*blocksize/total*50)
            self.sch=min(self.sch,50)

        def download(url,referer,path):
            self.opener.addheaders=[
                ('Accept-Language', 'zh-CN,zh;q=0.8'),
                ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'),
                ('Referer', referer)    #p站的防盗链机制
            ]
            pattern=re.compile(r'([a-zA-Z.0-9_-]*?)$')
            filename=re.search(pattern, url).group(0)
            if filename.find("master")!=-1:
                master=re.search(re.compile(r"_master[0-9]*"), filename)
                filename=filename.replace(master.group(0),"")
            self.filename=filename
            urllib.request.install_opener(self.opener)
            try:
                urllib.request.urlretrieve(url,path+filename,report) 
            except Exception as e:
                os.remove(path+filename)
                self.q.put((referer,url))
        while not self.exitflag:
            if not self.q.empty():
                links=self.q.get()
                self.is_working=True
                download(links[1],links[0],self.path)
                self.sch=0
                self.is_working=False


class mySpider: 
    def __init__(self):
        self.os_path=os.getcwd()+"\\"
        folder=time.strftime("%Y%m%d",time.localtime())
        self.max_dlthread=5
        self.url="http://www.pixiv.net/ranking.php?mode=daily"
        try:
            os.mkdir(self.os_path + folder)
        except:
            pass

        self.os_path=folder+"\\"
        self.picurl_list=Queue()
        self.rank_list=list()
        self.downlist=list()

    def login(self):
        os.system("cls")
        print("Now Logging in......")
        with open("babel.json","r") as f:
            babel=json.load(f)
        login_url=babel["url"]
        data=babel["data"]
        login_data=urllib.parse.urlencode(data).encode()
        login_header=babel["header"]
        request=urllib.request.Request(url=login_url,data=login_data,headers=login_header)
        
        cookie=http.cookiejar.MozillaCookieJar(".cookie")
        handler=urllib.request.HTTPCookieProcessor(cookie)
        opener=urllib.request.build_opener(handler)
        response=opener.open(request)
        print("Log in Successful.............")
        cookie.save(ignore_discard=True,ignore_expires=True)
        response.close()
        print("Update cookue Successful......")

    def cookie_opener(self):
        cookie=http.cookiejar.MozillaCookieJar()
        cookie.load(".cookie",ignore_discard=True,ignore_expires=True)
        handler=urllib.request.HTTPCookieProcessor(cookie)
        opener=urllib.request.build_opener(handler)
        return opener

    def crawl(self,opener):
        response=opener.open(self.url)
        html=response.read().decode("gbk","ignore")
        soup=BeautifulSoup(html,"html5lib")
        tag_a=soup.find_all("a")
        for link in tag_a:
            top_link=str(link.get("href"))
            if top_link.find("member_illust")!=-1:
                pattern=re.compile(r"id=[0-9]*")
                result=re.search(pattern, top_link)
                if result!=None:
                    result_id=result.group(0)
                    url_work="http://www.pixiv.net/member_illust.php?mode=medium&illust_"+result_id
                    if url_work not in self.rank_list:
                        self.rank_list.append(url_work)
        def _crawl():
            while len(self.rank_list)>0:
                url=self.rank_list[0]
                response=opener.open(url)
                html=response.read().decode("gbk","ignore")
                soup=BeautifulSoup(html,"html5lib")
                imgs=soup.find_all("img","original-image")
                if len(imgs)>0:
                    self.picurl_list.put((url,str(imgs[0]["data-src"])))
                else:
                    mutiple=soup.find_all("a"," _work multiple ")
                    if len(mutiple)>0:
                        manga_url="http://www.pixiv.net/"+mutiple[0]["href"]
                        response=opener.open(manga_url)
                        html=response.read().decode("gbk","ignore")
                        soup=BeautifulSoup(html,"html5lib")
                        imgs=soup.find_all("img","image ui-scroll-view")
                        for i in range(0,len(imgs)):
                            self.picurl_list.put((manga_url+"&page="+str(i),str(imgs[i]["data-src"])))
                self.rank_list=self.rank_list[1:]

        self.crawler=threading.Thread(target=_crawl)
        self.crawler.start()
        for i in range(0,self.max_dlthread):
            thread=downloader(self.picurl_list, self.os_path, opener)
            thread.start()
            self.downlist.append(thread)
        flag=False
        while not self.picurl_list.empty() or len(self.rank_list)>0 or not flag:
            os.system("cls")
            flag=True
            if len(self.rank_list)>0:
                print(str(len(self.rank_list))+" urls to parse...")
            if not self.picurl_list.empty():
                print(str(self.picurl_list.qsize())+" pics ready to download...")
            for t in self.downlist:
                if t.is_working:
                    flag=False
                    print("Downloading "+'"'+t.filename+'" : \t[' + ">"*t.sch + " "*(50-t.sch) + "] " + str(t.sch*2) + " %")
                else:
                    print("This downloader is not working now.")
            time.sleep(0.1)

        for t in self.downlist:
            t.exitflag=True

    def start(self):
        st=time.time()
        self.login()
        opener=self.cookie_opener()
        self.crawl(opener)
        ed=time.time()
        tot=ed-st
        intval=getTime(int(tot))
        os.system("cls")
        print("Finished")
        print("Total using "+intval+" .")


s =mySpider()


s.start()