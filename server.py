# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time
import socket
import time
import threading

# Import the PCA9685 module.
import Adafruit_PCA9685


# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 200  # Min pulse length out of 4096
servo_max = 500  # Max pulse length out of 4096

limited_min = 200
limited_max = 300
delta = limited_max - limited_min

channels = {
    "front-left": 0,
    "front-right": 1,
    "rear-left": 2,
    "rear-right": 3,
}

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 500       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

pwm.set_pwm_freq(60)
time.sleep(1)

UDP_IP = "0.0.0.0"
UDP_PORT = 1234

last_update = time.time()
initialization = False

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))

print("Listening ({}:{})".format(UDP_IP, UDP_PORT))

def stop():
    for channel in channels.values():
        pwm.set_pwm(channel, 0, limited_min)


def check():
    global last_update
    print("Safety thread is running")

    while True:
        if time.time() - last_update > 1 and not initialization:
            stop()
        time.sleep(0.1)

t1 = threading.Thread(target=check)
t1.start()

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message:", data)
    
    params = data.decode().strip().split()

    if params[0] == "init":
        last_update = time.time()
        initialization = True
        print("Initial")
        print("High")
        for channel in channels.values():
            pwm.set_pwm(channel, 0, servo_max)
        time.sleep(2)
        print("Low")
        for channel in channels.values():
            pwm.set_pwm(channel, 0, servo_min)
        time.sleep(0.5)
        initialization = False
        last_update = time.time()

    elif params[0] == "stop":
        stop()

    elif params[0] == "go":
        last_update = time.time()

        front_left = params[1]
        front_right = params[2]
        rear_left = params[3]
        rear_right = params[4]

        one_percent = delta / 100

        power_front_left = int(int(params[1]) * one_percent + limited_min)
        power_front_right = int(int(params[2]) * one_percent + limited_min)
        power_rear_left = int(int(params[3]) * one_percent + limited_min)
        power_rear_right = int(int(params[4]) * one_percent + limited_min)

        print("Front left", power_front_left)
        print("Front right", power_front_right)
        print("Rear left", power_rear_left)
        print("Rear right", power_rear_right)

        pwm.set_pwm(channels["front-left"], 0, power_front_left)
        pwm.set_pwm(channels["front-right"], 0, power_front_right)
        pwm.set_pwm(channels["rear-left"], 0, power_rear_left)
        pwm.set_pwm(channels["rear-right"], 0, power_rear_right)

        last_update = time.time()
        
#t1.join()
