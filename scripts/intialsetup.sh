#!/bin/bash

# raspberry pi configuration
# interfaces enable: SSH, VNC, I2C
# Reboot
# change password of account pi (passwd command)

echo "Starting Make Execute!"

sudo mkdir /usr/local/bin/cube

sudo chmod a+w /usr/local/bin/cube

sudo apt-get update
sudo apt-get install build-essential python-pip python-dev python-smbus git

cd /usr/local/bin/cube/AdafruitLibraries/Adafruit_Python_PCA9685-master
sudo python3 setup.py install

cd /usr/local/bin/cube/AdafruitLibraries/Adafruit_Python_GPIO-master
sudo python3 setup.py install



i2cdetect -y 1
# this should return 0x40 for the PWM HAT
