import os
import time
from dotenv import load_dotenv
from threading import Timer

# For HTTP server
import eventlet
import eventlet.wsgi
from flask import Flask, send_file

# For Socket.IO client
import socketio

# For MPU6050 (install via: pip install mpu6050)
# Alternative libraries may vary in usage
from MPU6050 import MPU6050


# Load environment variables from .env
load_dotenv()

# 1. HTTP Server Setup (Flask + eventlet)
app = Flask(__name__)

@app.route('/')
def index():
    """
    HTTP request handler similar to 'handler' in Node.js code.
    Reads and returns 'public/index.html'.
    Emits 'shooting' or 'hit' event depending on DEVICE_TYPE.
    """
    device_type = os.getenv('DEVICE_TYPE')
    pi_device_number = os.getenv('PI_DEVICE_NUMBER')

    # Emit shoot/hit event on every request, matching the Node.js behavior
    if device_type == 'gun':
        sio.emit('shooting', pi_device_number)
    else:
        sio.emit('hit', pi_device_number)

    # Serve the index.html file (adjust path if needed)
    try:
        return send_file('public/index.html')
    except:
        # Return a 404 if not found
        return '404 Not Found', 404

# 2. Socket.IO Client Setup
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to Socket.IO server.')
    device_type = os.getenv('DEVICE_TYPE')
    sword_name = os.getenv('SWORD_NAME')
    pi_device_number = os.getenv('PI_DEVICE_NUMBER')

    # Similar to socket.emit('initializeDevice', process.env.DEVICE_TYPE, process.env.SWORD_NAME)
    # We'll send a dict for clarity:
    sio.emit('initializeDevice', {'device_type': device_type, 'sword_name': sword_name})

    # Only set up GPIO watchers if not a sword
    if device_type != 'sword':
        setup_gpio_watchers()

    # Local test: automatically emit 'shooting' after 1.5s
    if os.getenv('NODE_ENV') == 'local':
        Timer(1.5, lambda: sio.emit('shooting', pi_device_number)).start()

@sio.event
def connect_error(err):
    # Matches Node.js 'connect_error' event
    print('Connection Error:', err)

@sio.event
def disconnect():
    print('Disconnected from Socket.IO server.')

@sio.on('hit')
def on_hit(data):
    """
    Matches Node.js:
    socket.on('hit', (data) => { ... })
    """
    print('Message from the server:', data)
    # Send a response back
    sio.emit('serverEvent', f"thanks server! for sending '{data}'")

    # If on Pi, blink LED
    if os.getenv('NODE_ENV') == 'pi':
        blink_led()

# 3. MPU6050 Setup and Reading
mpu = MPU6050.MPU6050(0x68)  # Default I2C address for MPU6050 is 0x68

mpu.reset();

mpu.gyro_config();

mpu.accel_config();

# We'll periodically read data, similar to setInterval in Node
def read_motion():
    """
    Periodically reads the motion data from the MPU6050.
    """
    try:
        accel_data = mpu.read_accelerometer()
        gyro_data = mpu.read_gyroscope()
        # If your library supports more advanced calls, adjust accordingly.
        print('Device data:', {'accel': accel_data, 'gyro': gyro_data})
    except Exception as e:
        print('Error reading motion data:', e)
    Timer(1, read_motion).start()

read_motion()  # start reading at 1-second intervals

# 4. GPIO Setup
# We'll replicate the Node.js pins:
#   LED on GPIO575 -> typically, Raspberry Pi numbering won't match 575, so adjust to your actual pin
#   maskDevice on GPIO577, chestPlateDevice on GPIO587, backPlateDevice on GPIO594, gunDevice on GPIO585
#
# In a real RPi, the highest BCM pin is 27 or 29 for Pi 4. So you'd need to map these carefully.
# For demonstration, let's assume you have them pinned to your local Pi's GPIO (with correct pins).
     # example physical pin


# 6. Socket.IO Connect
server_host = os.getenv('SERVER', 'localhost')
print('Connecting to server:', server_host)
sio.connect(f'http://{server_host}:3000', transports=['websocket'])

# 7. Run the HTTP server on port 8080
if __name__ == '__main__':
    print('Starting HTTP server on port 8080')
    eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
