#!/bin/bash

################################################################# Logfile

LOG_FILE="./arlo_usb_start.log"

if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi

echo "LogFile SUCCESS - 1/6" >> "$LOG_FILE"

################################################################# MaxPower

if [ -z "$1" ]; then
    echo "Usage: $0 <max_power>"
    exit 1
fi

MAX_POWER=$1

echo "MAX_POWER SUCCESS - 2/6" >> "$LOG_FILE"

################################################################# Dependencies

is_installed() {
    dpkg -l "$1" &> /dev/null
}

dependencies=(bash findutils util-linux rsync grep coreutils procps kmod)

for package in "${dependencies[@]}"; do
    if ! is_installed "$package"; then
        echo "Installing missing dependency: $package"
        sudo apt-get update
        sudo apt-get install -y "$package"
    fi
done

echo "Dependencies SUCCESS - 3/6">> "$LOG_FILE"

################################################################# DWC2

echo "dwc2" >> /etc/modules
echo "dtoverlay=dwc2" >> /boot/config.txt

echo "DWC2 SUCCESS - 4/6" >> "$LOG_FILE"

################################################################# Storage

ARLO_IMG_FILE=/arlo.bin
ARLO_IMG_SIZE=31457280
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
function add_drive () {
  local name="$1"
  local label="$2"
  local size="$3"
  local filename="$4"
  fallocate -l "$size"K "$filename"
  echo "type=c" | sfdisk "$filename" > /dev/null
  
  local partition_offset
  partition_offset=$(first_partition_offset "$filename")
  loopdev=$(losetup -o "$partition_offset" -f --show "$filename")
  mkfs.vfat "$loopdev" -F 32 -n "$label"
  losetup -d "$loopdev"
  local mountpoint=/mnt/"$name"
  if [ ! -e "$mountpoint" ]
  then
    mkdir "$mountpoint"
  fi
}
add_drive "arlo" "ARLO" "$ARLO_IMG_SIZE" "$ARLO_IMG_FILE" 

echo "Storage IMG SUCCESS - 5/6" >> "$LOG_FILE"

################################################################# Cronjob

init_mass_storage="@reboot sudo sh $(pwd)/cronsetup/enable_mass_storage.sh $MAX_POWER"
sync_clip_interval="*/1 * * * * sudo /bin/bash $(pwd)/cronsetup/sync_clips.sh"
cleanup_clips_interval="0 0 * * * sudo /bin/bash $(pwd)/cronsetup/cleanup_clips.sh"
( crontab -l | cat;  echo "$init_mass_storage" ) | crontab -
( crontab -l | cat;  echo "$sync_clip_interval" ) | crontab -
( crontab -l | cat;  echo "$cleanup_clips_interval" ) | crontab -
crontab -l

echo "Cronjob SUCCESS - 6/6" >> "$LOG_FILE"

#################################################################

sudo reboot now
