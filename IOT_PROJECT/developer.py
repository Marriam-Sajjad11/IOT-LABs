import network
import socket
import dht
import machine
import ssd1306  # OLED library
import time

# WiFi Configuration (Replace with your WiFi credentials)
SSID = "YourWiFiSSID"
PASSWORD = "YourWiFiPassword"

# Initialize WiFi in Station Mode
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass  # Wait for connection

print("Connected! IP Address:", wifi.ifconfig()[0])

# Initialize DHT11 Sensor
dht_pin = machine.Pin(4)  # GPIO4
dht_sensor = dht.DHT11(dht_pin)

# Initialize OLED Display
i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8))  
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize Buzzer
buzzer = machine.Pin(5, machine.Pin.OUT)  # GPIO5 for buzzer

# Default Alarm Status
alarm_active = False

# Function to Read Temperature & Humidity
def get_sensor_data():
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    return temp, hum

# Function to Update OLED Display
def update_oled(temp, hum, alarm):
    oled.fill(0)  # Clear screen
    oled.text("Temp: {} C".format(temp), 0, 0)
    oled.text("Humidity: {}%".format(hum), 0, 10)
    if alarm:
        oled.text("ALARM ON!", 0, 30)
    else:
        oled.text("System Normal", 0, 30)
    oled.show()

# Function to Control Buzzer
def activate_buzzer(state):
    if state:
        buzzer.value(1)
    else:
        buzzer.value(0)

# HTML Web Page
def generate_webpage(temp, hum, alarm):
    return """ 
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Buzzer Alert</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                background: linear-gradient(135deg, #1e3c72, #2a5298);
                color: white; 
                margin: 0; 
                padding: 0;
            }
            .container { 
                width: 80%; 
                margin: auto; 
                padding: 20px;
            }
            .card {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
                margin-bottom: 20px;
            }
            h1 {
                font-size: 28px;
                margin-bottom: 10px;
            }
            h2 {
                font-size: 22px;
                margin: 10px 0;
            }
            button {
                padding: 12px 20px;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                background: #ff9800;
                color: white;
                cursor: pointer;
                transition: 0.3s;
            }
            button:hover {
                background: #e68900;
            }
            .alert {color: #ff0000; font-weight: bold;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 Buzzer Alert System</h1>
            
            <div class="card">
                <h2> Temperature: """ + str(temp) + """°C</h2>
                <h2> Humidity: """ + str(hum) + """%</h2>
            </div>

            <div class="card">
                <h3> Alarm Status: """ + ("<span class='alert'>ON</span>" if alarm else "OFF") + """</h3>
                <a href="/?alarm=on"><button>Turn Alarm ON</button></a>
                <a href="/?alarm=off"><button>Turn Alarm OFF</button></a>
            </div>
        </div>
    </body>
    </html>
    """

# Start Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 80))
server.listen(5)

print("Web Server Started! Access it via browser.")

while True:
    conn, addr = server.accept()
    print("Client connected from", addr)
    
    request = conn.recv(1024).decode()
    
    # Check for Alarm Control in Request
    global alarm_active
    if "GET /?alarm=on" in request:
        alarm_active = True
    elif "GET /?alarm=off" in request:
        alarm_active = False

    # Get Sensor Data
    temp, hum = get_sensor_data()

    # Activate Buzzer if Alarm is ON & Conditions Are Met
    if alarm_active and (temp > 30 or hum > 80):
        activate_buzzer(True)
    else:
        activate_buzzer(False)

    # Update OLED Display
    update_oled(temp, hum, alarm_active)

    # Send Webpage Response
    response = generate_webpage(temp, hum, alarm_active)
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()
