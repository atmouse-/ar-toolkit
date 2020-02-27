#!/usr/bin/python

import sys
import os
from os import listdir
from os.path import isfile, join

import re

# snapshot and poweroff

def get_last_snapshot(snaps):
    cur = 0
    for s in snaps:
        try:
            cur_timestamp = int(re.findall("\d+", s)[0])
            if cur_timestamp > cur:
                cur = cur_timestamp
        except:
            continue
    if cur == 0:
        print("no snapshot found")
        sys.exit(1)
    return "rootfs-"+str(cur)

def get_min_snapshot(snaps):
    cur = 9999999999999999
    for s in snaps:
        try:
            cur_timestamp = int(re.findall("\d+", s)[0])
            if cur_timestamp < cur:
                cur = cur_timestamp
        except:
            continue
    if cur == 9999999999999999:
        print("no snapshot found")
        sys.exit(1)
    return "rootfs-"+str(cur)

def get_root_uuid():
    result = subprocess.check_output("findmnt / -o UUID -n", shell=True)
    result = result.decode('utf-8').strip()
    return result

if __name__ == "__main__":
    ROOT_UUID = get_root_uuid()
    UDISK_UUID = "7A1971D87759BD20"

    result = subprocess.check_output("blkid", shell=True)
    if result.find(ROOT_UUID.encode('utf-8')) < 0:
        print("root block not found, exit")
        sys.exit(1)
    if result.find(UDISK_UUID.encode('utf-8')) < 0:
        print("udisk block not found, exit")
        sys.exit(1)
    
    result = os.system('mount | grep " /mnt/root "')
    if result == 0:
        print("please unmount /mnt/root/")
        sys.exit(1)
    result = os.system('mount | grep " /mnt/udisk "')
    if result == 0:
        print("please unmount /mnt/udisk/")
        sys.exit(1)
    os.system("mount -o subvolid=5 /dev/disk/by-uuid/{} /mnt/root".format(ROOT_UUID))
    os.system("mount -o subvolid=5 /dev/disk/by-uuid/{} /mnt/udisk".format(UDISK_UUID))
    
    root_snapshot = [f for f in listdir("/mnt/root") if f.startswith("rootfs-")]
    udisk_snapshot = [f for f in listdir("/mnt/udisk/rootfs") if f.startswith("rootfs-")]
    _mixmax_snapshot = get_last_snapshot(root_snapshot and udisk_snapshot)
    _last_snapshot = get_last_snapshot(udisk_snapshot)

    if _last_snapshot > _mixmax_snapshot:
        cmd = "zcat /mnt/udisk/rootfs/{1}/{0}.gz | btrfs receive /mnt/root/".format(_mixmax_snapshot, _last_snapshot)
        print(cmd)
        os.system(cmd)
        os.system("sync")
        # 
        print("please:")
        print("create clone of {} to a new writeable snapshot as activefs-2019100811111-rw".format(_last_snapshot))
        print("then change systemd-boot param rootflags=subvol=activefs-2019100811111-rw")
        print("and reboot as possible")
        print("after all, clean old activefs rw snapshot")
    else:
        print("nothing to do")

    os.system("umount /mnt/root")
    os.system("umount /mnt/udisk")
