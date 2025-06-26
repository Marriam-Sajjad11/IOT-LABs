import network
import socket
import dht
import machine
import ssd1306  # OLED library
from neopixel import NeoPixel  # Import NeoPixel library

# WiFi Access Point Configuration
SSID = "ESP32_AP"
PASSWORD = "12345678"  # Minimum 8 characters required

# Initialize WiFi in AP Mode
wifi = network.WLAN(network.AP_IF)
wifi.active(True)
wifi.config(essid=SSID, password=PASSWORD)

print("Access Point Created!")
print("AP IP Address:", wifi.ifconfig()[0])

# Initialize DHT11 Sensor
dht_pin = machine.Pin(4)  # GPIO4
dht_sensor = dht.DHT11(dht_pin)

# Initialize OLED Display (SSD1306)
i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8))  
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize RGB LED (Built-in NeoPixel)
rgb_pin = machine.Pin(48, machine.Pin.OUT)  # Change pin if needed
rgb_led = NeoPixel(rgb_pin, 1)  # Only 1 LED on ESP32

# Function to Set RGB Color
def set_rgb_color(r, g, b):
    rgb_led[0] = (r, g, b)
    rgb_led.write()

# Function to Read Temperature & Humidity
def get_sensor_data():
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    return temp, hum

# Function to Update OLED Display
def update_oled(temp, hum, r, g, b):
    oled.fill(0)  # Clear screen
    oled.text("Temp: {} C".format(temp), 0, 0)
    oled.text("Humidity: {}%".format(hum), 0, 10)
    oled.text("RGB: R{} G{} B{}".format(r, g, b), 0, 30)
    oled.show()

# HTML Web Page
def generate_webpage(temp, hum):
    return """ 
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Web Server</title>
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
            input {
                padding: 12px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                text-align: center;
                width: 80px;
                margin: 5px;
                outline: none;
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 RGB LED & Sensor Web Server</h1>
            
            <div class="card">
                <h2> Temperature: """ + str(temp) + """°C</h2>
                <h2> Humidity: """ + str(hum) + """%</h2>
            </div>

            <div class="card">
                <h3> Set RGB Color</h3>
                <form action="/" method="GET">
                    <input type="number" name="r" placeholder="Red (0-255)" min="0" max="255">
                    <input type="number" name="g" placeholder="Green (0-255)" min="0" max="255">
                    <input type="number" name="b" placeholder="Blue (0-255)" min="0" max="255">
                    <br><br>
                    <button type="submit">Set Color</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# Start Web Server in AP Mode
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 80))
server.listen(5)

print("Web Server Started! Connect to '{}' and visit '192.168.4.1'".format(SSID))

while True:
    conn, addr = server.accept()
    print("Client connected from", addr)
    
    request = conn.recv(1024).decode()
    
    # Parse RGB Values
    r, g, b = 0, 0, 0  # Default values
    if "GET /?" in request:
        try:
            params = request.split(" ")[1].split("?")[1].split("&")
            r = int(params[0].split("=")[1])
            g = int(params[1].split("=")[1])
            b = int(params[2].split("=")[1])
            set_rgb_color(r, g, b)
        except:
            pass
    
    # Get Sensor Data
    temp, hum = get_sensor_data()

    # Update OLED Display
    update_oled(temp, hum, r, g, b)

    # Send Webpage Response
    response = generate_webpage(temp, hum)
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()
