#!/usr/bin/env python
# coding=utf-8
# @Date    : 2016-11-02 13:38:08
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import shutil
import glob
import time
  
 
#shutil.copy('hello.py','test1')

#shutil.copytree('test1','test2')

#shutil.move('hello2.py','test1\hello2.py')

#os.remove('test1\hello.py')

#os.remove('test2\hello.py')
#os.rmdir('test2')  #只能删除空目录

#shutil.rmtree('test1') #可删除非空目录
  


i=0
img_ext=['bmp','png','jpeg','gif','jpg']

def rename_Img(path):
	global i

	if not os.path.isdir(path) and not os.path.isfile(path):
		return False 
	if os.path.isfile(path):
		print 1
		lists=os.path.split(path)
		file_path=lists[0]
		file_info=lists[1].split('.')
		file_ext=file_info[1]
		file_name=file_info[0]
		if file_ext in img_ext:
			os.rename(path,file_path+'/'+file_name+'_ts'+'.'+file_ext)
			i+=1
	elif os.path.isdir(path): 
		print 2
		for x in os.listdir(path): 
			rename_Img(os.path.join(path,x))

def test():
	img_dir='e:\\Image'
	start=time.time()
	rename_Img(img_dir)
	c=time.time()-start
	print '程序运行共耗时：%0.5f' %c
	print '共处理图片：%s张' %i



 
if __name__ == '__main__':
	test()