#coding=utf-8
import os
import re
import time
import json
import threading
from os import sys
import urllib.request
import http.cookiejar
from queue import Queue
from bs4 import BeautifulSoup

def getTime(intvl):	#将一个以秒为单位的间隔转换为xx h xx m xx s的格式
	h = 0
	m = 0
	s = intvl
	if s > 60:
		m = s // 60
		s -= m * 60
	if m > 60:
		h = m // 60
		m -= h * 60
	return format("%02d h %02d m %02d s"%(h, m, s))

class downloader (threading.Thread):	#将一个下载器作为一个线程

	def __init__(self, q, path, opener):
		threading.Thread.__init__(self)
		self.opener = opener 	#下载器用的opener
		self.q = q #主队列
		self.sch = 0	#进度[0-50]
		self.is_working = False	#是否正在工作
		self.filename = ""	#当前下载的文件名
		self.path = path #文件路径
		self.exitflag = False #是否退出的信号

	def run(self):
		def report(blocks, blocksize, total):	#回调函数用于更新下载的进度
			self.sch = int(blocks * blocksize / total * 50)	#计算当前下载百分比
			self.sch = min(self.sch, 50)	#忽略溢出
		def download(url, referer, path):	#使用urlretrieve下载图片
			self.opener.addheaders = [	#给opener添加一个头
				('Accept-Language', 'zh-CN,zh;q=0.8'),
				('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'),
				('Referer', referer)	#p站的防盗链机制
			]
			pattern = re.compile(r'([a-zA-Z.0-9_-]*?)$')	#正则匹配处理模式
			filename = re.search(pattern, url).group(0)	#匹配图片链接生成本地文件名
			if filename.find("master") != -1:			#去除多图的master_xxxx的字符串
				master = re.search(re.compile(r'_master[0-9]*'), filename)
				filename = filename.replace(master.group(0), '')
			self.filename = filename
			urllib.request.install_opener(self.opener) #添加更新后的opener
			try:
				urllib.request.urlretrieve(url, path + filename, report) #下载文件到本地
			except:
				os.remove(path + filename) #如果下载失败，将问题文件删除，并将referer和url重新放入队列
				self.q.put((referer, url))
		while not self.exitflag:
			if not self.q.empty(): #当队列非空获取队列首部元素，开始下载
				links = self.q.get()
				self.is_working = True
				download(links[1], links[0], self.path)
				self.sch = 0															#置零
				self.is_working = False

class spider:

	def __init__(self):
		self.os_path = os.getcwd() + "\\"
		folder = time.strftime("%Y-%m-%d", time.localtime())	#获取年月日格式为 "Y-M-D" 例如: 2016-12-06
		self.max_dlthread = 5	#下载最大线程的数量(不要轻易修改，以免被ban)
		self.url = "http://www.pixiv.net/ranking.php?mode=daily"	#需要爬的链接(p站每日排行榜)
		try:
			os.mkdir(self.os_path + folder)	#尝试创建以年月日为名字的目录，如果存在则跳过
		except Exception as e:
			pass
		self.os_path += folder + "\\"	#更改操作路径
		self.picurl_queue = Queue()	#为了安全，这里改成队列了，存放带图片链接的referer和link，这是判断是否终止的第二层条件
		self.rankurl_list = list()	#这里是用来存放排行榜首页直接获取的link，直接用来判断是否该终止的第一层条件
		self.downlist = list()

	def login(self):
		os.system("cls")     #清屏
		print("Now logging in...")
		with open("babel.json", "r") as f: #改为用json存信息
			babel = json.load(f)
		login_url = babel["url"]	#登陆页面的网址
		data = babel["data"]
		login_data = urllib.parse.urlencode(data).encode()	#对请求进行编码
		login_header = babel["header"]
		request = urllib.request.Request(	#创建请求
			url=login_url,
			data=login_data,
			headers=login_header
		)
		cookie = http.cookiejar.MozillaCookieJar(".cookie") #创建cookie每次都覆盖，进行更新
		handler = urllib.request.HTTPCookieProcessor(cookie)
		opener = urllib.request.build_opener(handler)
		response = opener.open(request)
		print("Log in successfully!")
		cookie.save(ignore_discard=True, ignore_expires=True)
		response.close()
		print("Update cookies successfully!")
		time.sleep(1)

	def cookie_opener(self):	#使用cookie登陆, 创建opener
		cookie = http.cookiejar.MozillaCookieJar()
		cookie.load(".cookie", ignore_discard=True, ignore_expires=True)
		handler = urllib.request.HTTPCookieProcessor(cookie)
		opener = urllib.request.build_opener(handler)
		return opener

	def crawl(self, opener):	#构建一个urllist存放所有要下载的图片的链接
		response = opener.open(self.url)
		html = response.read().decode("gbk", "ignore")	#编码，忽略错误(错误一般不存在在链接上)
		soup = BeautifulSoup(html, "html5lib")	#使用bs和html5lib解析器，创建bs对象
		tag_a = soup.find_all("a")
		for link in tag_a:
			top_link = str(link.get("href"))	#找到所有<a>标签下的链接
			if top_link.find("member_illust") != -1:
				pattern = re.compile(r'id=[0-9]*')	#过滤存在id的链接
				result = re.search(pattern, top_link)
				if result != None:
					result_id = result.group(0)
					url_work = "http://www.pixiv.net/member_illust.php?mode=medium&illust_" + result_id
					if url_work not in self.rankurl_list:
						self.rankurl_list.append(url_work)
		def _crawl():
			while len(self.rankurl_list) > 0:
				url = self.rankurl_list[0]
				response = opener.open(url)
				html = response.read().decode("gbk", "ignore")	#编码，忽略错误(错误一般不存在在链接上)
				soup = BeautifulSoup(html, "html5lib")
				imgs = soup.find_all("img", "original-image")
				if len(imgs) > 0:
					self.picurl_queue.put((url, str(imgs[0]["data-src"])))
				else:
					multiple = soup.find_all("a", " _work multiple ")
					if len(multiple) > 0:
						manga_url = "http://www.pixiv.net/" + multiple[0]["href"]
						response = opener.open(manga_url)
						html = response.read().decode("gbk", "ignore")
						soup = BeautifulSoup(html, "html5lib")
						imgs = soup.find_all("img", "image ui-scroll-view")
						for i in range(0, len(imgs)):
							self.picurl_queue.put((manga_url + "&page=" + str(i), str(imgs[i]["data-src"])))
				self.rankurl_list = self.rankurl_list[1:]
		self.crawler = threading.Thread(target=_crawl) #开第一个线程用于爬取链接，生产者消费者模式中的生产者
		self.crawler.start()
		for i in range(0, self.max_dlthread): #根据设定的最大线程数开辟下载线程，生产者消费者模式中的消费者
			thread = downloader(self.picurl_queue, self.os_path, opener)
			thread.start()
			self.downlist.append(thread) #将产生的线程放入一个队列中
		flag = False
		while not self.picurl_queue.empty() or len(self.rankurl_list) > 0 or not flag:
			#显示进度，同时等待所有的线程结束，结束的条件(这里取相反)：
			#1 下载队列为空
			#2 解析列表为空
			#3 当前所有的下载任务完成
			os.system("cls")
			flag = True
			if len(self.rankurl_list) > 0:
				print(str(len(self.rankurl_list)) + " urls to parse...")
			if not self.picurl_queue.empty():
				print(str(self.picurl_queue.qsize()) + " pics ready to download...")
			for t in self.downlist:
				if t.is_working:
					flag = False
					print("Downloading " + '"' + t.filename + '" : \t[' + ">"*t.sch + " "*(50-t.sch) + "] " + str(t.sch*2) + " %")
				else:
					print("This downloader is not working now.")
			time.sleep(0.1)
		
		for t in self.downlist: #结束后给每一个下载器发送一个退出指令
			t.exitflag = True

	def start(self):
		st = time.time()
		self.login()
		opener = self.cookie_opener()
		self.crawl(opener)
		ed = time.time()
		tot = ed - st
		intvl = getTime(int(tot))
		os.system("cls")
		print("Finished.")
		print("Total using " + intvl  + " .") #统计全部工作结束所用的时间

pixiv_spider = spider()
pixiv_spider.start()