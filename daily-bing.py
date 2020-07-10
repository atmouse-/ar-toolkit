#!/usr/bin/python

import urllib  
import urllib.request
import re  
import time  
import os
import shutil
import json
import hashlib
import fnmatch

from io import BytesIO
from PIL import Image
from libqtile.sh import QSh
from libqtile import command
from os.path import expanduser
from libsway import Sway

from liboguri import OguriConfig


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

def fetch_bing_bg():
    html = urllib.request.urlopen("https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US").read().decode('utf-8')
    _j = json.loads(html)
    _url = _j['images'][0]['url']
    url = "http://cn.bing.com" + _url
    return BytesIO(
        urllib.request.urlopen(url).read()
    )

def sha256sum(filepath):
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def sha256sum_io(fd):
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    fd.seek(0)
    while True:
        data = fd.read(BUF_SIZE)
        if not data:
            break
        sha256.update(data)
    fd.seek(0)
    return sha256.hexdigest()

def clean_oguri_wallpaper():
    for rootDir, subdirs, filenames in os.walk('/home/atmouse/.config/oguri/wallpaper/'):
        # Find the files that matches the given patterm
        for filename in fnmatch.filter(filenames, '*.jpg'):
            try:
                os.remove(os.path.join(rootDir, filename))
            except OSError:
                print("Error while deleting file")

def oguri_set_bg(imagepath):
    # reload config
    conf = OguriConfig()
    conf.set_output_image("*", imagepath)
    os.system("/sbin/ogurictl output --image {} \*".format(imagepath))

if __name__ == '__main__':  
    start=time.time()  
    #home = expanduser("~")
    #if os.path.isfile(home + "/.config/qtile/wall.jpg"):
    #    shutil.copyfile(home + "/.config/qtile/wall.jpg", "/tmp/bing_bg.jpg")
    bg_image = fetch_bing_bg()
    end=time.time()  
    print('done %.2f seconds' % (end-start))
    clean_oguri_wallpaper()
    wallpaper = "/home/atmouse/.config/oguri/wallpaper/{}.jpg".format(sha256sum_io(bg_image))
    with open(wallpaper, "wb") as f:
        f.write(bg_image.read())
        f.flush()
    #sway = Sway()
    #sway.sway_set_bg(wallpaper)
    oguri_set_bg(wallpaper)
