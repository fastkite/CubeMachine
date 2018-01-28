import maestro
import time

servo = maestro.Controller()
#servo.setAccel(0,4)      #set servo 0 acceleration to 4
#servo.setRange(0,900,2100)  #set servo to move to center position

for i in (1000,1200,1400,1600,1800,2000,4000,6000,8000):

    servo.setTarget(0,i)  #set servo to move to center position
    print ("location:",i)
    print ("get position,",servo.getPosition(0))
    time.sleep(1)



servo.close