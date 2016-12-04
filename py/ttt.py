#!/usr/bin/env python
import sys
import time
import struct
import uinput
import serial

try:
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=19200
    )
except:
    print("Opening serial port failed")
    sys.exit(1)
ser.isOpen()
time.sleep(2)
time.sleep(0.5)
print("DUMP")
msg = struct.pack("=B", 4)
ser.write(msg)
time.sleep(0.1)
data = ser.read(7)
res = struct.unpack("=BHHH", data)
print(res)

print("ENABLE")
ser.write(struct.pack("=B", 1))
time.sleep(1)
print("DISABLE")
ser.write(struct.pack("=B", 2))

time.sleep(0.5)
print("DUMP")
msg = struct.pack("=B", 4)
ser.write(msg)
time.sleep(0.1)
data = ser.read(7)
res = struct.unpack("=BHHH", data)
print(res)
