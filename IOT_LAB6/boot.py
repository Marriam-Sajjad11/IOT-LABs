# setup static ip for esp32

import network
import utime as time

WIFI_SSID = 'Shaham'
WIFI_PASS = 'hadia123'

# Static IP configuration
STATIC_IP = "192.168.27.217"
SUBNET_MASK = "255.255.255.0"
GATEWAY = "192.168.27.151"
DNS_SERVER = "8.8.8.8"



print("Connecting to WiFi network '{}'".format(WIFI_SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

wifi.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS_SERVER))

wifi.connect(WIFI_SSID, WIFI_PASS)
while not wifi.isconnected():
    time.sleep(1)
    print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])