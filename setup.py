from distutils.core import setup
import os, sys
import glob

import py2exe

setup(name='OpenTiler',
      version="0.1",
      description = "OpenTiler",
      long_description= "OpenTiler generates Zoomify tiles and a viewer for supplied images (TIFF, JPEG, BMP, GIF,..). Batch mode is supported (you can choose more files in the first dialog or call the script form the BAT file) and watermarking is possible.",
      url='https://github.com/moravianlibrary/opentiler/',
      author='Klokan Petr Pridal',
      author_email='klokan@klokan.cz',
      console=['opentiler.py','watermark.py'],
       options={'py2exe':{
           'unbuffered': True,
           'includes':['encodings','EasyDialogs','PIL.Image','PIL.ImageEnhance','urllib2'],
           'excludes':['Tkinter', 'email.Generator', 'email.Iterators', 'email.Utils'],
       }
      },
      data_files=[("data", ["data/ZoomifyViewer.swf", "data/OpenLayers.js"]),
      ("data\img", glob.glob("data\\img\\*"))],
)
