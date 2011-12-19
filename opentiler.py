#!/usr/bin/env python
# encoding: utf-8
"""
OpenTiler
=========
Based on my pil2zoomify.py prototype. The gdal2zoomify.py is available as well (for tiling huge TIFFs, SIDs, ECWs, ...).

This script is using EasyDialogs for GUI, and needs installed PIL (Python Imaging Library), beside the Python.

Created by Petr Přidal on 2010-01-26.
Copyright (c) 2010 Klokan Petr Pridal (www.klokan.cz). All rights reserved.
"""
import EasyDialogs

#from pil2zoomify import main 
#from zoomify import Zoomify

import math, os
import shutil

from progress_bar import ConsoleProgressBar


class Zoomify(object):
	"""
	Tiles compatible with the Zoomify viewer
	"""

	def __init__(self, width, height, tilesize = 256, tileformat='jpg'):
		"""Initialization of the Zoomify tile tree"""
		
		self.tilesize = tilesize
		self.tileformat = tileformat
		imagesize = ( width, height )
		tiles = ( math.ceil( width / float(tilesize) ), math.ceil( height / float(tilesize) ) )

		# Size (in tiles) for each tier of pyramid.
		self.tierSizeInTiles = []
		self.tierSizeInTiles.append( tiles )

		# Image size in pixels for each pyramid tier
		self.tierImageSize = []
		self.tierImageSize.append( imagesize );

		while (imagesize[0] > tilesize or imagesize[1] > tilesize ):
			imagesize = ( int(math.floor( imagesize[0] / 2.0 )), int(math.floor( imagesize[1] / 2.0)) )
			tiles = ( int(math.ceil( imagesize[0] / float(tilesize) )), int(math.ceil( imagesize[1] / float(tilesize))) ) 
			self.tierSizeInTiles.append( tiles )
			self.tierImageSize.append( imagesize )

		self.tierSizeInTiles.reverse()
		self.tierImageSize.reverse()
	
		# Depth of the Zoomify pyramid, number of tiers (zoom levels)
		self.numberOfTiers = len(self.tierSizeInTiles)
											
		# Number of tiles up to the given tier of pyramid.
		self.tileCountUpToTier = []
		self.tileCountUpToTier.append(0)
		for i in range(1, self.numberOfTiers+1):
			self.tileCountUpToTier.append(
				self.tierSizeInTiles[i-1][0] * self.tierSizeInTiles[i-1][1] + self.tileCountUpToTier[i-1]
			)		
	
	def tilefilename(self, x, y, z):
		"""Returns filename for tile with given coordinates"""
		
		tileIndex = x + y * self.tierSizeInTiles[z][0] + self.tileCountUpToTier[z]
		return os.path.join("TileGroup%.0f" % math.floor( tileIndex / 256.0 ),
			"%s-%s-%s.%s" % ( z, x, y, self.tileformat))

# ------
import Image, ImageEnhance
from random import randrange

import ArgImagePlugin
import BmpImagePlugin
import CurImagePlugin
import DcxImagePlugin
import EpsImagePlugin
import FliImagePlugin
import FpxImagePlugin
import GbrImagePlugin
import GifImagePlugin
import IcoImagePlugin
import ImImagePlugin
import ImtImagePlugin
import IptcImagePlugin
import JpegImagePlugin
import McIdasImagePlugin
import MicImagePlugin
import MpegImagePlugin
import MspImagePlugin
import PalmImagePlugin
import PcdImagePlugin
import PcxImagePlugin
import PdfImagePlugin
import PixarImagePlugin
import PngImagePlugin
import PpmImagePlugin
import PsdImagePlugin
import SgiImagePlugin
import SunImagePlugin
import TgaImagePlugin
import TiffImagePlugin
import WmfImagePlugin
import XVThumbImagePlugin
import XbmImagePlugin
import XpmImagePlugin


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def write_jpeg(path, dstile, dswatermark ):
	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	if dswatermark:
		dsmark = Image.new('RGBA', dstile.size, (0,0,0,0))	
		# empty random range bug fix
		end0 = dstile.size[0]-dswatermark.size[0]
		end1 = dstile.size[1]-dswatermark.size[1]
		if end0 > 0 and end1 > 0:
			dsmark.paste(dswatermark, (randrange(0, end0), randrange(0, end1)))
			dstile = Image.composite(dsmark, dstile, dsmark)
	dstile.save(path, "JPEG", quality=85)




def create_root(rootPath, exepath, zoomifyViewer):
	if not os.path.exists(rootPath):
		os.makedirs(rootPath)
	srcDirectory = os.path.join(exepath, 'data')
	srcFile = "OpenLayers.js"
	if zoomifyViewer:
		srcFile = "ZoomifyViewer.swf"
	else:
		imgFolder = os.path.join(srcDirectory, "img")
		imgDstFolder = os.path.join(rootPath, "img")	
		if not os.path.exists(imgDstFolder):	
			 shutil.copytree(imgFolder, imgDstFolder)
	src = os.path.join(srcDirectory, srcFile)
	dst = os.path.join(rootPath, srcFile)
	shutil.copyfile(src, dst)

def get_exepath():
	exepath = os.getcwd()
	if hasattr(sys, "frozen"):
		exepath = os.path.dirname(sys.executable)
	return exepath



def tile(filename, dialogbar, rootPath, exepath, zoomifyViewer, current, total):
	# open input file
	ds = Image.open(filename)
	width, height = ds.size	
	zoomify = Zoomify( width, height )
	tilecount = zoomify.tileCountUpToTier[zoomify.numberOfTiers]
	divider = tilecount // 40
	
	
	if dialogbar:
		dialogProgressbar = EasyDialogs.ProgressBar("Tiling file %s / %s" % (current, total), 100, "Processing the image:\n%s" % filename)
		dialogProgressbar.set(0, tilecount)
	else:
		prefix = "[" + str(current) + "/" + str(total) + "]"
		#suffix = filename	
		suffix = ""
		consoleProgressbar = ConsoleProgressBar(prefix, suffix, 1, tilecount, 50, mode='fixed', char='#')

	if os.path.exists( os.path.join(exepath, "watermark.png")):
		dswatermark = reduce_opacity( Image.open( os.path.join(exepath, "watermark.png")), 0.1 )
	else:
		dswatermark = None
			
	# create folder for the image
	folderName =  os.path.basename(os.path.splitext(filename)[0])
	path = os.path.join(rootPath, folderName)
	if not os.path.exists(path):
		os.makedirs(path)
	
	# write ImageProperties.xml
	f = open(os.path.join(path,"ImageProperties.xml"),"w")
	f.write("""<IMAGE_PROPERTIES WIDTH="%d" HEIGHT="%d" NUMTILES="%d" NUMIMAGES="1" VERSION="1.8" TILESIZE="256" />""" %
		( width, height, tilecount))

	# Write the "index.html" with eather openLayers viewer of zoomify viewer
	viewerText = None
	if zoomifyViewer:
		viewerText = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
   <title>%s</title>   
      <meta http-equiv="content-type" content="text/html; charset=utf-8" />
      <meta http-equiv="content-language" content="en" />
        <style type="text/css">
           body {
	      margin:0;
	      padding:0;
           }    
	   .link {
	      position:absolute; 
	      top: 0px; 
	      left: 0px;
	      color: #fff;
	      z-index: -1; 
	   }           
        </style>    
</head>
<body>
  <center>
    <OBJECT CLASSID="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" CODEBASE="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" WIDTH="100%%" HEIGHT="100%%" ID="theMovie">
      <PARAM NAME="FlashVars" VALUE="zoomifyImagePath=.">
      <PARAM NAME="MENU" VALUE="FALSE">
      <PARAM NAME="SRC" VALUE="../ZoomifyViewer.swf">
	<EMBED FlashVars="zoomifyImagePath=." SRC="../ZoomifyViewer.swf" MENU="false" PLUGINSPAGE="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash"  WIDTH="100%%" HEIGHT="100%%" NAME="theMovie"></EMBED>
    </OBJECT>
  </center>
  <a href="http://help.oldmapsonline.org/" class="link">Old Maps Online.org</a>
</body></html>"""  % (folderName)

	else:
	      viewerText = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>%s</title>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <meta http-equiv="content-language" content="en" />
        <style type="text/css">
           body {
	      margin:0;
	      padding:0;
           }    
	   .link {
	      position:absolute; 
	      top: 0px; 
	      left: 0px;
	      color: #fff;
	      z-index: -1; 
	   }           
        </style>    
    <script src="../OpenLayers.js"></script>    

<script type="text/javascript">
  function init(){	
    var width = %d;
    var height = %d;
    var zoomify = new OpenLayers.Layer.Zoomify("Zoomify", "./", new OpenLayers.Size(width, height));	       
    var options = {
	controls: [],
	maxExtent: new OpenLayers.Bounds(0, 0, width, height),
	maxResolution: Math.pow(2, zoomify.numberOfTiers-1),
	numZoomLevels: zoomify.numberOfTiers,
	units: 'pixels'
    };
    
    var map = new OpenLayers.Map("map", options);
    map.addLayer(zoomify);
    map.addControl(new OpenLayers.Control.PanZoomBar());
    map.addControl(new OpenLayers.Control.MouseDefaults());
    map.addControl(new OpenLayers.Control.KeyboardDefaults());

    map.setBaseLayer(zoomify);
    map.zoomToMaxExtent();
  };
</script>

</head>
  <body onload="init()">
    <div id="map"></div>
    <a href="http://help.oldmapsonline.org/" class="link">Old Maps Online.org</a>
  </body>
</html>""" % (folderName, width, height)

	f = open(os.path.join(path,"index.html"),'w')
	f.write(viewerText)
	f.close()

	#import urllib2
	#urlf = urllib2.urlopen("ttp://www.oldmapsonline.org/publish/zoomify/ZoomifyViewer.swf","rb")
	#f = open(os.path.join(path,"ZoomifyViewer.swf"),'wb')
	#f.write( urlf.read() )
	#f.close()	
	# generate base tiles

	tileno = 0

	for z in range(zoomify.numberOfTiers-1, -1, -1):
		width, height = zoomify.tierImageSize[z]
		if ds.size != (width, height):
			ds = ds.resize( (width, height), Image.ANTIALIAS )
		for y in range(0, height, 256):
			for x in range(0, width, 256):
				tileWidth, tileHeight = 256, 256
				if x+256 > width:
					tileWidth = width % 256
				if y+256 > height:
					tileHeight = height % 256
				#print x/256, y/256, x, y, tileWidth, tileHeight
			
				dstile = Image.new('RGB', (tileWidth, tileHeight))
				dstile.paste( ds, (-x,-y) )
				write_jpeg(os.path.join(path, zoomify.tilefilename(x/256, y/256, z)), dstile, dswatermark )
				tileno += 1
				if dialogbar:
					dialogProgressbar.inc()
				else:
					consoleProgressbar.increment_amount()
					consoleProgressbar.print_bar()

				#	print ".", 
				# gdal.TermProgress_nocb(tileno/tilecount)



	if dialogbar:
		del dialogProgressbar
	else:
		del consoleProgressbar
	print
	#import webbrowser
	#webbrowser.open_new(os.path.join(path,"index.html"))


def usage():
	print """
    usage: python opentiler.py [OPTION]... [FILE]...

    options:
        -z, --zoomify             use Zoomify Viewer instead of OpenLayers
        -h, --help                display this help and exit
	-o, --output <STRING>     path to the output directory
	
	"""

def main():	
	import getopt            

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hzo:', ['output=', 'help', 'zoomify'])

	except getopt.error, msg:
		print str(msg)
		usage();
		sys.exit(2)

	exepath = get_exepath()
	# without -z => openLayers
	# with -z => zoomifyViewer
	zoomifyViewer = False
	dialog_bar = True
	outputPath = None
	for option, arg in opts:
		if option in ('--help', '-h'):
			usage()
			sys.exit()
		if option in ('--zoomify', '-z'):
			zoomifyViewer = True
		elif option in ('--output', '-o'):
			outputPath = arg
				
	if len(args) > 0:
		filenames = args[0:]
		if outputPath:
			dialog_bar = False
	else:
		filenames = []
		try:
			filenames = EasyDialogs.AskFileForOpen("Choose one or more files you want to process", multiple=True)
		except:	
			file = EasyDialogs.AskFileForOpen()
			if file:
				filenames.append(file)

	if not outputPath:
		outputPath = EasyDialogs.AskFolder("Choose folder for output.")
	rootPath = os.path.join(outputPath, 'output')
	create_root(rootPath, exepath, zoomifyViewer)
	fileno = len(filenames)
	i = 0		
	for file in filenames:			
			if file == None:
				continue
			i += 1		
			tile(file, dialog_bar, rootPath, exepath, zoomifyViewer, i, fileno)




if __name__ == "__main__":
	import sys
	
	main()