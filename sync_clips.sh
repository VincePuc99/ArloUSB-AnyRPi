#!/bin/bash

#needed for expose the mnt arlo to share without corrupting any data

for pid in $(pidof -x sync_clips.sh); do
    if [ $pid != $$ ]; then
        echo "[$(date)] : Process is already running"
        exit 1
    fi
done

ARLO_IMG_FILE=/arlo.bin

function first_partition_offset () {
  local filename="$1"
  local size_in_bytes
  local size_in_sectors
  local sector_size
  local partition_start_sector

  size_in_bytes=$(sfdisk -l -o Size -q --bytes "$1" | tail -1)
  size_in_sectors=$(sfdisk -l -o Sectors -q "$1" | tail -1)
  sector_size=$(( size_in_bytes / size_in_sectors ))
  partition_start_sector=$(sfdisk -l -o Start -q "$1" | tail -1)

  echo $(( partition_start_sector * sector_size ))
}

umount /mnt/arlo || true
partition_offset=$(first_partition_offset "$ARLO_IMG_FILE")
loopdev=$(losetup -o "$partition_offset" -f --show "$ARLO_IMG_FILE")
mount "$loopdev" /mnt/arlo

# Create the directory if it doesn't exist
mkdir -p /mnt/ArloExposed

rsync -avu --delete "/mnt/arlo/" "/mnt/ArloExposed"
umount /mnt/arlo || true
losetup -d "$loopdev"

