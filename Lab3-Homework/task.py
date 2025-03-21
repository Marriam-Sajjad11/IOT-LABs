from machine import Pin, I2C  # Import necessary modules for microcontroller pins and I2C communication
import ssd1306  # Import the OLED display driver
import dht  # Import the DHT sensor library
import utime  # Import time module for delays

# ---------------------- Task 1: Displaying Temperature & Humidity on OLED ----------------------

# Initialize I2C for OLED (Modify pins according to your board)
i2c = I2C(0, scl=Pin(8), sda=Pin(9))  # Raspberry Pi Pico (Use GPIO 5 for SCL, GPIO 4 for SDA)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # Initialize the OLED display with 128x64 resolution

# Initialize DHT11 sensor for temperature and humidity
dht_sensor = dht.DHT11(Pin(14))  # Connect DHT11 data pin to GPIO14

def display_message(msg):
    """
    Function to display a message on the OLED screen.
    """
    oled.fill(0)  # Clear the screen
    oled.text(msg, 0, 20)  # Display the message at position (0,20)
    oled.show()  # Update the OLED screen

# ---------------------- Task 2: Running the Code Without Interrupt ----------------------

def read_sensor():
    """
    Reads temperature and humidity from the DHT11 sensor.
    Returns temperature and humidity values.
    """
    try:
        dht_sensor.measure()  # Trigger sensor reading
        temp = dht_sensor.temperature()  # Get temperature
        hum = dht_sensor.humidity()  # Get humidity
        return temp, hum  # Return values
    except:
        return None, None  # Return None in case of an error

# ---------------------- Task 3: Understanding Debounce Issue ----------------------

# Initialize a button for interrupt handling
button_pressed = False  # A flag to track button state

# Interrupt handler function
def button_interrupt(pin):
    """
    This function is triggered when the button is pressed.
    It sets the button_pressed flag to True.
    """
    global button_pressed
    button_pressed = True

# Set up the button with an interrupt on falling edge (button press)
button = Pin(15, Pin.IN, Pin.PULL_UP)  # Button connected to GPIO15 with pull-up resistor
button.irq(trigger=Pin.IRQ_FALLING, handler=button_interrupt)  # Attach interrupt handler

# ---------------------- Task 4: Why Do We Use Interrupts? ----------------------
"""
Why do we use interrupts?
- Without interrupts, the microcontroller must **constantly check** (poll) the button state in the loop.
- Polling wastes processing time and is **inefficient** for real-time applications.
- Interrupts allow the microcontroller to **focus on other tasks** and respond to events only when needed.

How does an interrupt lower the processing cost of the microcontroller?
- Instead of looping to check button status, the processor can **stay idle or perform other tasks**.
- When the button is pressed, an **interrupt occurs**, and the processor only then executes the required action.
- This **reduces CPU load** and improves efficiency.
"""

while True:
    # Read sensor values
    temp, hum = read_sensor()

    # Display sensor values on OLED if valid
    if temp is not None and hum is not None:
        oled.fill(0)  # Clear the screen
        oled.text("Temp: {}C".format(temp), 0, 20)  # Display temperature
        oled.text("Hum: {}%".format(hum), 0, 35)  # Display humidity
        oled.show()  # Update OLED display

    # ---------------------- Task 3: Understanding Debounce Issue ----------------------

    # Check for button press interrupt
    if button_pressed:
        display_message("Button Pressed!")  # Display message when button is pressed
        utime.sleep(1)  # Simple debounce delay to avoid multiple triggers
        button_pressed = False  # Reset the flag

    utime.sleep(2)  # Read sensor every 2 seconds
