# KStat Graphical Interface

Graphical web interface hosted on a Raspberry Pi to control a KStat potentiostat for voltammetric measurements using Python3 scripts.

## Hotspot Access

RaspAP (https://github.com/billz/raspap-webgui) is configured to provide access to the web interface through a WiFi hotspot.

WiFi ID: VoltammetryPi

Password: eigentlich!

Web Interface: voltammetrypi.local:8080

## Frontend/Backend Communication

The program consists of two main parts: The front end serving the GUI to the user to accept commands and settings and display data and the back end to control the KStat as well as stirring and purging. The front and back end are connected using a redis server implemented in python using the redisworks package for simplification.

## Frontend (Dash by Plotly)

The frontend is programmed as a Dash app (https://plotly.com/dash/) hosted locally on port 8080.

### Updating GUI components

GUI components are updated using a Dash interval component set to 250ms. During every update interval, the configuration is loaded from the redis server. The state of every component is compared to the configuration and updated if it's different. 

Components that can be updated through user input have an additional placeholder component that is updated when a change in the configuration is detected to differentiate whether the update occurred through user input or through updates from the back end. Otherwise every configuration change would trigger the associated callback function for the updated component. 