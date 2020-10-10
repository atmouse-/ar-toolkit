#!/usr/bin/python

import sys
import os
import subprocess
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

def prepare_udisk(uuid):
    retcode = os.system("mount -o noatime,nodiratime /dev/disk/by-uuid/{} /mnt/udisk".format(uuid))
    if retcode != 0:
        print("mount udisk fs error")
        sys.exit(1)

def prepare_udisk_luks(uuid):
    cmd = "cryptsetup open /dev/disk/by-uuid/{} root-lexar".format(uuid)
    retcode = os.system(cmd)
    if retcode != 0:
        print("decrypt udisk error")
        sys.exit(1)
    retcode = os.system("mount -o subvolid=5 /dev/disk/by-id/dm-name-root-lexar /mnt/udisk")
    if retcode != 0:
        print("mount decrypt udisk error")
        sys.exit(1)

if __name__ == "__main__":
    ROOT_UUID = get_root_uuid()
    UDISK_UUID = "7342e6e4-39ee-48c2-9012-e5e54bce7c5b"
    UDISK_TYPE = "crypto_LUKS"

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
    if UDISK_TYPE == "crypto_LUKS":
        prepare_udisk_luks(UDISK_UUID)
    else:
        prepare_udisk(UDISK_UUID)

    root_snapshots = [f for f in listdir("/mnt/root") if f.startswith("rootfs-")]
    udisk_snapshots = [f for f in listdir("/mnt/udisk") if f.startswith("rootfs-")]
    _mixmax_snapshot = get_last_snapshot(list(set(root_snapshots).intersection(udisk_snapshots)))
    prepare_snapshots = [f for f in udisk_snapshots if f > _mixmax_snapshot]
    _last_snapshot = get_last_snapshot(udisk_snapshots)

    if prepare_snapshots:
        if UDISK_TYPE == "crypto_LUKS":
            for _snapshot in prepare_snapshots:
                cmd = "btrfs send -p /mnt/udisk/{0} /mnt/udisk/{1} | btrfs receive /mnt/root/".format(_mixmax_snapshot, _snapshot)
                print(cmd)
                print("Press Enter to continue:", end="")
                input()
                os.system(cmd)
                _mixmax_snapshot = _snapshot
                os.system("sync")
        else:
            for _snapshot in prepare_snapshots:
                cmd = "zcat /mnt/udisk/{1}/{0}.gz | btrfs receive /mnt/root/".format(_mixmax_snapshot, _snapshot)
                print(cmd)
                print("Press Enter to continue:", end="")
                input()
                os.system(cmd)
                _mixmax_snapshot = _snapshot
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

    if UDISK_TYPE == "crypto_LUKS":
        os.system("cryptsetup close root-lexar")
