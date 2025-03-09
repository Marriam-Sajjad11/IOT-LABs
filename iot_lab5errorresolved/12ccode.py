from machine import Pin, I2C
import time

# Define I2C pins (Try GPIO22 for SCL and GPIO21 for SDA if needed)
i2c = I2C(1, scl=Pin(9), sda=Pin(8), freq=100000)  

print("Scanning for I2C devices...")
time.sleep(1)

devices = i2c.scan()  # Scan for connected I2C devices

if devices:
    print("I2C devices found:", [hex(device) for device in devices])
else:
    print("No I2C devices found. Check wiring!")
