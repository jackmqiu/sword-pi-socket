import time
import board
import adafruit_mpu6050
import socketio
import threading

sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=5,       # number of attempts
    reconnection_delay=1,         # seconds delay between attempts
    reconnection_delay_max=5      # max seconds between attempts
)

i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)
dataOn = False
thread = None


def emit_data():
    global dataOn
    while dataOn:
        sio.emit('deviceData', {'data': mpu.acceleration + mpu.gyro})
        time.sleep(0.01)


@sio.event
def connect():
    print("connected to socket server")
    sio.emit('initializeDevice', {'deviceType': 'sword', 'swordName': 'yellow'})


@sio.event
def disconnect():
    print("disconnected from server")


@sio.on('dataOn')
def on_data_on():
    global dataOn, thread
    if not dataOn:
        dataOn = True
        thread = threading.Thread(target=emit_data)
        thread.start()


@sio.on('dataOff')
def on_data_off():
    global dataOn
    dataOn = False


if __name__ == '__main__':
    try:
        sio.connect('http://192.168.86.34:3000')
        sio.wait()
    except Exception as e:
        print(f"connect error: {e}")
    finally:
        dataOn = False
        if thread:
            thread.join()
        if sio.connected:
            sio.disconnect()
