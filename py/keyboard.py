#!/usr/bin/env python
import sys
import time
import struct
import uinput
import serial

button_map = [
    uinput.KEY_0,
    uinput.KEY_1,
    uinput.KEY_2,
    uinput.KEY_3,
    uinput.KEY_4,
    uinput.KEY_5,
    uinput.KEY_6,
    uinput.KEY_7,
    uinput.KEY_8,
    uinput.KEY_9,
]

try:
    keydev = uinput.Device(button_map, name="numericRotary")
except PermissionError:
    print("ERROR: need to run as root")
    sys.exit(1)

try:
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=19200
    )
except:
    print("Opening serial port failed")
    sys.exit(1)
ser.isOpen()
time.sleep(0.1)

while True:
    key_raw = ser.read(1)
    key = struct.unpack("=B", key_raw)[0]
    if key in range(0,10):
        keydev.emit_click(button_map[key])
    time.sleep(0.05)
