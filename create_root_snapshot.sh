#!/bin/sh

# check /mnt/root dir exist and empty
[ -d /mnt/root ] || exit 1
[ "x$(ls -A /mnt/root 2>/dev/null)" == "x" ] || exit 1

# check /mnt/root no mount
cat /etc/mtab | awk '{print $2}' | grep -E "^/mnt/root/?" && exit 1

# checkif subvolume exist
ROOT_UUID=$(findmnt / -o UUID -n || exit 1)

# mount btrfs to /mnt/root
mount -o subvolid=5 /dev/disk/by-uuid/${ROOT_UUID} /mnt/root || exit 1

# check current rootfs not subvolid 5
btrfs subvolume show / | grep "Subvolume ID" | grep -E "\b5\b" && exit 1


SNAPSHOT="rootfs-"$(date +%Y%m%d%H%M)

# check if cur snapshot dir exist
ls /mnt/root | grep $SNAPSHOT && exit 1

# create snapshot
btrfs subvolume snapshot -r / /mnt/root/$SNAPSHOT

echo "Create btrfs snapshot done."

# umount /mnt/root
umount /mnt/root
