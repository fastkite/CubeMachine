
# run this command to get the pigpio service started
#  sudo systemctl enable pigpiod.service


import pigpio
import time

pi = pigpio.pi()
bus = 1
address = 0x2c

handle = pi.i2c_open(bus, address)

while True:
    for i in range (64):
        packet = [0x00,i]
        pi.i2c_write_device(handle, packet)
        print (i)
        time.sleep(5)


pi.i2c_close(handle)