
import pigpio
import time

pi = pigpio.pi()
servopin = 18
relaypin = 27

min = 800
max = 2200



print ("relay off")
pi.write(relaypin,0)


print ("servo to minimum")
pi.set_servo_pulsewidth(servopin, min)
time.sleep(5)


print ("relay on")
pi.write(relaypin,1)


for i in range (min, max, 1):
    val = 1000
    pi.set_servo_pulsewidth(servopin, i)
    print (i)
    time.sleep(0.01)


#pi.set_servo_pulsewidth(servopin, min)
time.sleep(5)
pi.set_servo_pulsewidth(servopin, min)
time.sleep(5)

print ("relay off")
pi.write(relaypin,0)
print ("servo to minimum")
pi.set_servo_pulsewidth(servopin, 0)