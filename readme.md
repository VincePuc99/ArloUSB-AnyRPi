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