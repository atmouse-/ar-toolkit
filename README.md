## Prepare udisk
```
sudo -s
mount /dev/${UDISK} /mnt/udisk
mkdir -p /mnt/udisk/rootfs
mkdir -p /mnt/udisk/rootfs/{CURRENT_ROOTFS_BTRFS_SNAPSHOT}
```

## Create root snapshot
```
sudo create_root_snapshot.sh
```

## Sync btrfs snapshot to udisk
```
sudo btrkeep_save_udisk.py
```

## Sync back to current system
```
sudo btrkeep_restore_udisk.py
```

## Switch to the newer snapshot
```
sudo optiplex_reset_last_snapshot.sh
```