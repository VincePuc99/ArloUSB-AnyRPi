# Arlo USB-RPi Setup

This project provides scripts to set up and manage an Arlo USB storage system on a Raspberry Pi.<br />The scripts handle tasks such as enabling mass storage (30GB), synchronizing clips, cleaning up old clips and optionally create a service for synchronizing clips with a Telegram Bot.

All clips are stored in `/mnt/ArloExposed`. You need to access this folder to expose them on your preferred service (GDrive - Samba - Telegram).


#### ⚠️ WARNING ⚠️
Two folders will be created in `/mnt` - `/arlo` and `/ArloExposed`. To avoid data corruption, DO NOT TOUCH the `arlo` one.<br />
Tested on RPi-4B 8GB and RPi-Zero2W both on [DietPi](https://dietpi.com/) Bookworm.

### What you need

For RPi Zero/Zero2W:
- Connect the USB cable to the middle port from the RPi (Without the PWR label) to the USB of the station, Arlo base station itself is enough to power the Raspbery Pi.



For others RPi's:
- Connect the USB cable to any USB port of the RPi, you will need an external power source.


## Installation


### Cloning the Repository
To clone this repository, use the following command:

```sh
git clone git@github.com:VincePuc99/ArloUSB-AnyRPi.git
```

### Permissions

```sh
cd /ArloUSB-AnyRPi
```
```sh
sudo chmod +x *
```

### Starting the Setup

To start the setup, run the `Arlo-Usb-Start.sh` script with the appropriate args for your Raspberry Pi model.

#### Optional - Sync with Telegram Bot (python3)

This Python script monitors `/mnt/ArloExposed/arlo/000000` for new video files and sends them to your Telegram bot. It uses the bot's API token and the chat ID to send the videos.

#### Prerequisites for Telegram Sync

- Python 3.x
- A Telegram bot with the API token (created via BotFather)
- The chat ID of the Telegram chat where the videos will be sent.

### Usage

```sh
sudo ./Arlo-Usb-Start.sh <max_power> <TelYes|TelNo> [api_token] [chat_id]
```
Where <max_power> is:

- `500` for Raspberry Pi 4
- `200` for Raspberry Pi Zero 2
- `100` for Raspberry Pi Zero

Example for Raspberry Pi 4 with Telegram Sync Enabled:
```
./Arlo-Usb-Start.sh 500 TelYes 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 -zzzzzzzzzz
```
Example for Raspberry Pi 4 without Telegram Sync:
```
./Arlo-Usb-Start.sh 500 TelNo
```

After running `Arlo-Usb-Start.sh`, the Raspberry Pi will reboot. Upon reboot, check the connection to the base in Arlo Secure App.
If you chose `TelNo`, the `telegram-sync.py` file will be automatically deleted.

## Documentation

- `Arlo-Usb-Start.sh` - This script installs necessary dependencies and runs the other scripts in the correct order. It ensures that the system is properly set up for USB mass storage and clip management. | Main script to start the setup process.

- `cleanup_clips.sh` - Cleans up old clips from the storage directory. By default, it removes clips older than 14 days.

- `enable_mass_storage.s` - Enables USB mass storage with the specified maximum power.

- `sync_clips.sh` - Synchronizes clips from the USB storage to a shared directory. Ensures that the mount point is properly managed to avoid data corruption.

- `telegram-sync.py`: (Optional) File service for synchronizing clips from the USB storage to a Telegram Bot.

### Dependencies
The scripts require the following packages:

- `bash`
- `findutils`
- `util-linux`
- `rsync`
- `grep`
- `coreutils`
- `procps`
- `kmod`

The Arlo-Usb-Start.sh script will automatically install these dependencies if they are not already installed.

## License
This project is licensed under the MIT License.
