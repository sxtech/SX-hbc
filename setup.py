# coding: utf-8

from distutils.core import setup
import py2exe
import sys

#this allows to run it with a simple double click.

sys.argv.append('py2exe')

script = [{

    "script":"d:/Python27/project/hbc/SX-hbcview.py", 

    'icon_resources':[(1, 'd:/Python27/project/hbc/logo.ico'),]

    }]

 

py2exe_options = {

        "includes":["sip",],

        "dll_excludes": ["MSVCP90.dll",]

        }

 

setup(windows=script, options={'py2exe':py2exe_options})
