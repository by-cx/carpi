import socket
from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/event19')

UDP_IP = "192.168.1.34"
UDP_PORT = 1234
 
print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP


def go(front_left, front_right, rear_left, rear_right):
    cmd = "go {} {} {} {}".format(
        front_left,
        front_right,
        rear_left,
        rear_right,
    )
    print(cmd)
    sock.sendto(cmd.encode(), (UDP_IP, UDP_PORT))

def stop():
    sock.sendto("stop".encode(), (UDP_IP, UDP_PORT))
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
MIN_POWER = 200

power = 0
left_mod = 1
right_mod = 1

for event in dev.read_loop():
    if event.code == 304:
        init()
    elif event.code == 0 and event.value == 0:
        continue
    elif event.code == 9:
        print("Trigger (%):", event.value/MAX)
        power = MAX_DIFF * event.value/MAX
        if power < 10:
            stop()
            continue
    elif event.code == 0:
        if event.value < HALF:
            print("Stick left:", (HALF - event.value)/HALF)
            left_mod = 1-(HALF - event.value)/HALF
        elif event.value > HALF:
            print("Stick right:", (event.value - HALF)/HALF)
            right_mod = 1-(event.value-HALF)/HALF

    if power < 0.1 * MAX_DIFF:
        stop()
    else:
        go(
            int((power*right_mod) + MIN_POWER),
            int((power*left_mod) + MIN_POWER),
            int((power*right_mod) + MIN_POWER),
            int((power*left_mod) + MIN_POWER),
        )

    #if event.type == ecodes.EV_KEY:
    #    print(categorize(event))
