
import CubeServo

class CubeArm(object):
    def __init__(self,
                 pwmObj, # pwm hat can control all servos to control all servos
                 channel, # pwm channel this servo is on
                 inDegree,
                 outDegree,
                ):





        self.inDegree = inDegree

        self.outDegree = outDegree

        self.servo = CubeServo.CubeServo(pwmObj=pwmObj, channel=channel,
                                         normalDegrees = 180,
                                         minNormalPulse = 0.6,
                                        maxNormalPulse = 2.4,
                                        minExtremePulse = 0.5,
                                        maxExtremePulse = 2.5)
        self.setOut()


    def setIn(self):
        self.servo.setDegree(self.inDegree)

    def setOut(self):
        self.servo.setDegree(self.outDegree)





# arm test program
if __name__ == "__main__":
    import Adafruit_PCA9685
    import time

    pwm = Adafruit_PCA9685.PCA9685()
    # Set frequency to 60hz, good for servos.
    pwm.set_pwm_freq(55) # WIERD!!! setting freq to 55 makes the actual frequency 60 hertz!

    arm = CubeArm(pwmObj= pwm, channel = 0, inDegree = 20, outDegree = -60)

    time.sleep(5)
    arm.setIn()
    time.sleep(5)
    arm.setOut()
    time.sleep(5)
    arm.setIn()
    time.sleep(5)
