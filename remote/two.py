import socket
import time
import threading
from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/by-id/usb-NVIDIA_Corporation_NVIDIA_Controller_v01.04-event-joystick')

UDP_IP = "192.168.19.1"
UDP_PORT = 1234
 
print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP


speed = [0, 0, 0, 0]

def set_speed(front_left, front_right, rear_left, rear_right):
    global speed
    print("Set speed: ", front_left, front_right, rear_left, rear_right)
    speed = [
        front_left,
        front_right,
        rear_left,
        rear_right,
    ]

def go(front_left, front_right, rear_left, rear_right):
    #print("Send GO command:", front_left, front_right, rear_left, rear_right)
    cmd = "go {} {} {} {}".format(
        front_left,
        front_right,
        rear_left,
        rear_right,
    )
    sock.sendto(cmd.encode(), (UDP_IP, UDP_PORT))

def stop():
    #sock.sendto("stop".encode(), (UDP_IP, UDP_PORT))
    set_speed(0, 0, 0, 0)
    print("stop")

def init():
    sock.sendto("init".encode(), (UDP_IP, UDP_PORT))

# 10 - left trigger - 0 to 65536
# 9 - right trigger - 0 to 65536
# 0 - left stick X - zero is 32768, max 65536
# 1 - left stick Y - zero is 32768, max 65536

MAX = 65536.0
HALF = 32768.0

MAX_DIFF = 100
MIN_POWER = 0

power = 0
left_mod = 1
right_mod = 1

def speed_loop():
    while True:
        go(speed[0], speed[1], speed[2], speed[3])
        time.sleep(0.05)

t1 = threading.Thread(target=speed_loop)
t1.start()

for event in dev.read_loop():
    #print(event)
    if event.code == 304:
        init()
    elif event.code == 0 and event.value == 0:
        continue
    # Left trigger
    elif event.code == 10:
        print("Break Trigger (%):", event.value/MAX)
        power = - MAX_DIFF * event.value/MAX
        if power > -10:
            stop()
            continue

        print("Power:", power)

    # Right trigger
    elif event.code == 9:
        print("Throttle Trigger (%):", event.value/MAX)
        power = MAX_DIFF * event.value/MAX
        if power < 10:
            stop()
            continue
        print("Power:", power)

    elif event.code == 0:
        if event.value < HALF:
            print("Stick left:", (HALF - event.value)/HALF)
            left_mod = (HALF - event.value)/HALF
            right_mod = -left_mod
        elif event.value > HALF:
            print("Stick right:", (event.value - HALF)/HALF)
            right_mod = (event.value-HALF)/HALF
            left_mod = -right_mod
        else:
            right_mod = 1
            left_mod = 1
        if left_mod < 0.1 and left_mod > -0.1:
            left_mod = 1
        if right_mod < 0.1 and right_mod > -0.1:
            right_mod = 1
        print("Left mod", left_mod)
        print("Right mod", right_mod)
    # left
    elif event.code == 310 and event.value == 1:
        set_speed(-80, 80, -80, 80)
        continue
    # left
    elif event.code == 311 and event.value == 1:
        set_speed(80, -80, 80, -80)
        continue
    elif event.code in (310, 311) and event.value == 0:
        stop()
        continue
        
    set_speed(
        int((power*left_mod) + MIN_POWER),
        int((power*right_mod) + MIN_POWER),
        int((power*left_mod) + MIN_POWER),
        int((power*right_mod) + MIN_POWER),
    )

    #if power < 0.1 * MAX_DIFF and power > -0.1 * MAX_DIFF:
    #    stop()
    #else:
    #if event.type == ecodes.EV_KEY:
    #    print(categorize(event))
