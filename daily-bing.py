#!/usr/bin/python

import urllib
import urllib.request
import re
import time
import os
import shutil
import json

from PIL import Image
from libqtile.sh import QSh
from libqtile import command
from os.path import expanduser
from libsway import Sway


def getHtml(url):
    return urllib.request.urlopen(url).read().decode('utf-8')

def getImgUrl(html):
    j = json.loads(html)
    url = j['images'][0]['url']
    return("http://cn.bing.com"+url)

def downloadImg(url,path):
    xpath=path+'/bing_bg.jpg'
    print(xpath)
    urllib.request.urlretrieve(url,xpath)

def calc_avgcolor(filepath):
    img = Image.open(filepath)
    size = img.size
    max_occurence, most_present = 0, 0
    try:
        for c in img.getcolors(size[0]*size[1]):
            if c[0] > max_occurence:
                (max_occurence, most_present) = c
        print(most_present)
        ret = "".join(["#",
                      "{:X}".format(most_present[0]).zfill(2),
                      "{:X}".format(most_present[1]).zfill(2),
                      "{:X}".format(most_present[2]).zfill(2),
                      ]).upper()
        return ret
    except TypeError:
        raise Exception("Too many colors in the image")

def qtile_reload_barcolor(color):
    c = command.Client()
    q = QSh(c)
    q.do_cd("bar")
    q.do_cd("top")
    print("set color:{}".format(color))
    cmd = "eval(\"self.background=\'{0}\'\")".format(color)
    q.process_command(cmd)
    return True

def qtile_apply_bg():
    os.system("feh --bg-fill /tmp/bing_bg.jpg")
    color = calc_avgcolor("/tmp/bing_bg.jpg")
    qtile_reload_barcolor(limit_color(color))
    os.remove("/tmp/bing_bg.jpg")

def limit_color(color):
    scolor = color.lstrip('#')
    if sum(tuple(int(scolor[i:i+2], 16) for i in (0, 2 ,4))) > 600:
        return "#C8C8C8"
    return color

if __name__ == '__main__':
    start=time.time()
    home = expanduser("~")
    if os.path.isfile(home + "/.config/qtile/wall.jpg"):
        shutil.copyfile(home + "/.config/qtile/wall.jpg", "/tmp/bing_bg.jpg")
    else:
        html=getHtml('https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US')
        url=getImgUrl(html)
        downloadImg(url,'/tmp')
    end=time.time()
    print('done %.2f seconds' % (end-start))
    wallpaper = "/home/atmouse/.config/wallpaper.jpg"
    shutil.move("/tmp/bing_bg.jpg", wallpaper)
    sway = Sway()
    sway.sway_set_bg(wallpaper)
