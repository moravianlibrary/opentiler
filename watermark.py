#!/usr/bin/env python
# encoding: utf-8
"""
OpenTiler Watermark
===================
This is a simple script which asks for the text and create a watermark.png file via Google Chart API

Created by Petr Pridal on 2010-01-26.
Copyright (c) 2010 Klokan Petr Pridal (www.klokan.cz). All rights reserved.
"""
import EasyDialogs
import sys, os

# Where is the executable file on the disk?
exepath = os.getcwd()
if hasattr(sys, "frozen"):
	exepath = os.path.dirname(sys.executable)

text = EasyDialogs.AskString("Text for the watermark (following copyright mark)\nBest is to use your 'domain.org' name in lowercase\n(leave empty for no watermark):")

if text:
	print "http://chart.apis.google.com/chart?chst=d_text_outline&chld=FFFFFF|11|h|000000|b|©%20"+text
	import urllib2
	urlf = urllib2.urlopen("http://chart.apis.google.com/chart?chst=d_text_outline&chld=FFFFFF|11|h|000000|b|%C2%A9%20" + urllib2.quote(text), 'rb')
	f = open(os.path.join(exepath,"watermark.png"),'wb')
	f.write( urlf.read() )
	f.close()
else:
	os.remove("watermark.png")
