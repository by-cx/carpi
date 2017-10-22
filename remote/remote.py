#!/usr/bin/python3

import socket
import readchar
import sys


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
 
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
    sock.sendto(cmd.encode(), (UDP_IP, UDP_PORT))

def stop():
    sock.sendto("stop".encode(), (UDP_IP, UDP_PORT))

def init():
    sock.sendto("init".encode(), (UDP_IP, UDP_PORT))

while True:
    key = readchar.readkey()
    if key == "q":
        sys.exit(0)
    elif key == "w":
        go(50, 50, 50, 50)
    elif key == "s":
        stop()
    elif key == "a":
        go(0, 50, 0, 50)
    elif key == "d":
        go(50, 0, 50, 0)
    elif key == "e":
        stop()
    elif key == "i":
        init()
    else:
        stop()
