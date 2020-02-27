## Prepare udisk (Machine megx570)
```
sudo -s
mount /dev/${UDISK} /mnt/udisk
mkdir -p /mnt/udisk/rootfs
mkdir -p /mnt/udisk/rootfs/{CURRENT_ROOTFS_BTRFS_SNAPSHOT}
```

## Create root snapshot (Machine megx570)
```
sudo create_root_snapshot.sh
```

## Sync btrfs snapshot to udisk (Machine megx570)
```
sudo btrkeep_save_udisk.py
```

**Remove Udisk from megx570 and connect to Machine optiplex**

## Sync back to current system (Machine optiplex)
```
sudo btrkeep_restore_udisk.py
```

## Switch to the newer snapshot (Machine optiplex)
```
sudo optiplex_reset_last_snapshot.sh
```

**reboot**