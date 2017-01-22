#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-10-28 11:49:26
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from gevent import monkey; monkey.patch_all()
import gevent
import urllib2

def f(url):
	print 'GET: %s' % url
	resp=urllib2.urlopen(url)
	data=resp.read()
	print '%d bytes received from %s.' %(len(data),url)

gevent.joinall([
	gevent.spawn(f,'https://www.github.com'),
	gevent.spawn(f,'https://www.yahoo.com'),
	gevent.spawn(f,'https://www.python.org'),
	])