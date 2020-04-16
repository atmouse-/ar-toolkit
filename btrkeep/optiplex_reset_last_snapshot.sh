#!/bin/sh

# check /mnt/root dir exist and empty
[ -d /mnt/root ] || exit 1
[ "x$(ls -A /mnt/root 2>/dev/null)" == "x" ] || exit 1

# check /mnt/root no mount
cat /etc/mtab | awk '{print $2}' | grep -E "^/mnt/root/?" && exit 1

# checkif subvolume exist
[ -e /dev/disk/by-uuid/ac4e124b-ad99-4392-b162-c82fb2975efc ] || exit 1

# checkif boot exist
[ -e /dev/disk/by-uuid/AF95-DC3C ] || exit 1

# checkif /boot mounted
findmnt /boot -o UUID -fn | grep AF95-DC3C || exit 1

# mount btrfs to /mnt/root
mount -o subvolid=5 /dev/disk/by-uuid/ac4e124b-ad99-4392-b162-c82fb2975efc /mnt/root || exit 1

# check current rootfs not subvolid 5
btrfs subvolume show / | grep "Subvolume ID" | grep -E "\b5\b" && exit 1


LAST_SNAPSHOT=$(ls -1 /mnt/root | grep rootfs- | sort -h | tail -1)
if [ "x$LAST_SNAPSHOT" = "x" ]
then
    echo "err: last snapshot not found"
    exit 1
fi

SNAPSHOT="activefs-"$(date +%Y%m%d%H%M)"-rw"

if [ -e /mnt/root/$SNAPSHOT ]
then
    echo "snapshot already exit"
    exit 1
fi

# create snapshot
btrfs subvolume snapshot /mnt/root/${LAST_SNAPSHOT} /mnt/root/$SNAPSHOT

echo "Create New $SNAPSHOT btrfs snapshot done."

# umount /mnt/root
umount /mnt/root

cat /boot/loader/entries/arch-optiplex-staging.conf | perl -pe "s/rootflags=subvol=\/activefs-\d+-rw/rootflags=subvol=\/${SNAPSHOT}/" > /tmp/arch-optiplex-staging.conf
mv /tmp/arch-optiplex-staging.conf /boot/loader/entries/arch-optiplex-staging.conf
chmod 755 /boot/loader/entries/arch-optiplex-staging.conf

#pushd efistub-wrapper
#cat main.c | perl -pe "s/activefs-\d+-rw/${SNAPSHOT}/" > /tmp/main.c
#mv /tmp/main.c main.c
#make clean
#make
#make install
#popd
#sync

## boot to linux next-time
#BOOTNUM=$(efibootmgr | grep "Arch Linux Optiplex" | awk '{print $1}' | grep -oP '\d+')
#efibootmgr --bootnext ${BOOTNUM}

echo -en "Press Enter to reboot now.."
read -r
reboot
