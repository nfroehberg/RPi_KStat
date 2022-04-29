# KStat Graphical Interface

Graphical web interface hosted on a Raspberry Pi to control a KStat potentiostat for voltammetric measurements using Python3 scripts.

## Setup

### Preparing the Pi

I use a Raspberry Pi 3b+ to host the GUI. It should also work on the Pi 4 but need adjustment of the USB address for the KStat in KStat_Dash_Back.py.

A fresh installation of Rapberry Pi OS is recommended.

The hostname should be changed to voltammetrypi in 

```li
sudo raspi-config
```

 or adjusted to the chosen name in KStat_Dash_Front.py. The interface will then be accessible at http://<hostname>.local:8080 .

#### Installing required packages

```
sudo apt install libatlas-base-dev redis git screen python3-pip

pip3 install scipy numpy peakutils matplotlib pandas plotly dash dash-daq dash-bootstrap-components redisworks smbus2 pyyaml pyserial dash_extensions
```

#### Setting up the Redis server

A redis server with default address (host = 127.0.0.1, port = 6379) is used to exchange commands and settings between the front end serving the GUI to the user and the backend controlling the KStat and peripherals.

Create redis configuration file and adjust:

```
sudo cp /etc/redis/redis.conf /etc/redis/6379.conf

sudo nano /etc/redis/6379.conf
```

Adjust 

```
save 900 1

save 300 10

save 60 10000
```

to

```
save 60 1

save 30 10

save 10 10000
```

This shortens the interval to save changes on the redis server to disk (optional). Startup of redis server needs to be added to rc.local (see next section). In python, the redisworks package (https://github.com/seperman/redisworks) is used for simplification of commands.

#### Installing the GUI

```
git config --global user.email “your.email@example.com”

git config --global user.name “Your Name”

git clone https://github.com/nfroehberg/RPi_KStat.git

sudo nano /etc/rc.local
```

rc.local is executed at boot of the Pi and can be used to autostart scripts and programs.

Add to beginning of file:

```
exec 1>/tmp/rc.local.log 2>&1 # send stdout and stderr from rc.local to a log file

set -x             # tell sh to display commands before execution
```

add to end before exit 0:

```
# start redis server and python scripts for KStat Dash interface

sleep 10 

redis-server /etc/redis/6379.conf

# if the Rpi_KStat/ folder is not located in the /home/pi directory, adjust address in the following lines:

su - pi -c "screen -dmS dash_back python3 RPi_KStat/KStat_Dash_Back.py"

su - pi -c "screen -dmS dash_front python3 RPi_KStat/KStat_Dash_Front.py"

# uncomment the following lines and comment out the previous two to have output of scripts logged to file on disk

#su - pi -c "screen -dmS dash_front -L -Logfile RPi_KStat/front.log python3 RPi_KStat/KStat_Dash_Front.py"

#su - pi -c "screen -dmS dash_back -L -Logfile RPi_KStat/back.log python3 RPi_KStat/KStat_Dash_Back.py"
```

#### WiFi hotspot

For ease of operation, particularly in situations where you don't have access to router settings in the network you use the Pi in, it is racommended to use a WiFi hotspot using the integrated WiFi module of the Pi with RaspAP (https://github.com/billz/raspap-webgui). Installation:

```
curl -sL https://install.raspap.com | bash -s -- --yes
```
 
 
 change port for RaspAP GUI:
 ```
 sudo nano /etc/lighttpd/lighttpd.conf
 ```
 change server.port to 8079
  ```
 sudo systemctl restart lighttpd.service
 ```

go to http://voltammetrypi.local/ (or http://<your hostname>.local/), login with username admin, password and set up hotspot SSID, password etc.

To still provide internet access to the user when connected to the hotspot, the Pi can be connected via ethernet or a USB WiFi adapter (for example the TP-Link TL-WN725N worked well).

To use a USB WiFi adapter, the RaspAP configuration needs two small adjustments:

```
sudo nano /var/www/html/includes/config.php
```

change wlan0 to wlan1 in

```
define('RASPI_WIFI_CLIENT_INTERFACE', 'wlan1')
```

and

```
sudo nano  /etc/dhcpcd.conf
```

insert 

```
interface wlan0

static ip_address=10.3.141.1/24

static domain_name_servers=1.1.1.1

nohook wpa_supplicant
```

and reboot the Pi.

## Frontend (Dash by Plotly)

The frontend is programmed as a Dash app (https://plotly.com/dash/) hosted locally on port 8080.

### Updating GUI components

GUI components are updated using a Dash interval component set to 250ms. During every update interval, the configuration is loaded from the redis server. The state of every component is compared to the configuration and updated if it's different. 

Components that can be updated through user input have an additional placeholder component that is updated when a change in the configuration is detected to differentiate whether the update occurred through user input or through updates from the back end. Otherwise every configuration change would trigger the associated callback function for the updated component. 
