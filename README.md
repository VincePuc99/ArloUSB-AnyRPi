# Arlo USB Setup

This project provides scripts to set up and manage an Arlo USB storage system on a Raspberry Pi. The scripts handle tasks such as enabling mass storage, synchronizing clips, and cleaning up old clips.

## Files

- `Arlo-Usb-Start.sh`: Main script to start the setup process.
- `cleanup_clips.sh`: Script to clean up old clips from the storage.
- `enable_mass_storage.sh`: Script to enable USB mass storage.
- `sync_clips.sh`: Script to synchronize clips from the USB storage to a shared directory.

## Usage

### Starting the Setup

To start the setup, run the `Arlo-Usb-Start.sh` script with the appropriate power setting for your Raspberry Pi model:

```sh
./Arlo-Usb-Start.sh <max_power>
```
Where <max_power> is:

- `500` for Raspberry Pi 4
- `200` for Raspberry Pi Zero 2
- `100` for Raspberry Pi Zero

Example for Raspberry Pi 4:
```
./Arlo-Usb-Start.sh 500
```

### Scripts
- `Arlo-Usb-Start.sh` - This script installs necessary dependencies and runs the other scripts in the correct order. It ensures that the system is properly set up for USB mass storage and clip management.

- `cleanup_clips.sh`
Cleans up old clips from the storage directory.
By default, it removes clips older than 14 days.

- `enable_mass_storage.s`
Enables USB mass storage with the specified maximum power.

- `sync_clips.sh`
Synchronizes clips from the USB storage to a shared directory.
Ensures that the mount point is properly managed to avoid data corruption.

### Dependencies
The scripts require the following packages:

bash
findutils
util-linux
rsync
grep
coreutils
procps
kmod

The Arlo-Usb-Start.sh script will automatically install these dependencies if they are not already installed.

License
This project is licensed under the MIT License.
