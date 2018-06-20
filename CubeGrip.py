
import CubeServo

class CubeGrip(object):
    def __init__(self,
                 pwmObj, # pwm hat can control all servos to control all servos
                 channel, # pwm channel this servo is on
                 forwardDegree,
                 middleDegree,
                 backDegree,
                ):





        self.forwardDegree = forwardDegree

        self.middleDegree = middleDegree

        self.backDegree = backDegree

        self.servo = CubeServo.CubeServo(pwmObj=pwmObj, channel=channel,
                                         normalDegrees=270,
                                         minNormalPulse=0.5,
                                         maxNormalPulse=2.5,
                                         minExtremePulse=0.4,
                                         maxExtremePulse=2.5)
        self.setMiddle()


    def setMiddle(self):
        self.servo.setDegree(self.middleDegree)

    def setBack(self):
        self.servo.setDegree(self.backDegree)

    def setForward(self):
        self.servo.setDegree(self.forwardDegree)




# arm test program
if __name__ == "__main__":
    import Adafruit_PCA9685
    import time

    pwm = Adafruit_PCA9685.PCA9685()
    # Set frequency to 60hz, good for servos.
    pwm.set_pwm_freq(55) # WIERD!!! setting freq to 55 makes the actual frequency 60 hertz!

    grip = CubeGrip(pwmObj= pwm, channel = 4, forwardDegree = 90, middleDegree = 0, backDegree = -90)

    time.sleep(5)
    grip.setForward()
    time.sleep(5)
    grip.setMiddle()
    time.sleep(5)
    grip.setBack()
    time.sleep(5)
