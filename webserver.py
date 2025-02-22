import os
from dotenv import load_dotenv
import socketio
import eventlet
import eventlet.wsgi
from flask import Flask, send_file
from hx711 import HX711
from gpiozero import LED, Button
from threading import Timer



load_dotenv()

# Flask setup for HTTP server
app = Flask(__name__)

@app.route('/')
def index():
    device_type = os.getenv('DEVICE_TYPE')
    pi_device_number = os.getenv('PI_DEVICE_NUMBER')

    if device_type == 'gun':
        sio.emit('shooting', pi_device_number)
    else:
        sio.emit('hit', pi_device_number)

    return send_file('public/index.html')

# Socket.IO client setup
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')
    device_type = os.getenv('DEVICE_TYPE')
    sword_name = os.getenv('SWORD_NAME')
    pi_device_number = os.getenv('PI_DEVICE_NUMBER')

    sio.emit('initializeDevice', {'device_type': device_type, 'sword_name': sword_name})

   
@sio.event
def connect_error(data):
    print('Connection failed:', data)

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('hit')
def on_hit(data):
    print('Message from server:', data)
    sio.emit('serverEvent', f"thanks server! for sending '{data}'")
    if os.getenv('NODE_ENV') == 'pi':
        blink_led()


# HX711 setup
hx711 = HX711(dout_pin=5, pd_sck_pin=6)
hx711.set_offset(50000)
hx711.set_scale(0.00001)

def read_strain():
    gauge_data = hx711.get_weight_mean(5)
    print('strain data:', gauge_data)
    Timer(1, read_strain).start()

read_strain()

# Start Socket.IO client
sio.connect(f"http://{os.getenv('SERVER')}:3000", transports=['websocket'])

# Run HTTP server
eventlet.wsgi.server(eventlet.listen(('', 8080)), app)
