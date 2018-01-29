
import CubeSide
import Adafruit_PCA9685
import time

class CubeMachine(object):
    def __init__(self):

        self.pwm = Adafruit_PCA9685.PCA9685()
        # Set frequency to 60hz, good for servos.
        self.pwm.set_pwm_freq(55)  # WIERD!!! setting freq to 55 makes the actual frequency 60 hertz!

        # channel   side         servo
        # 0         bottom       arm
        # 1         right        arm
        # 2         top          arm
        # 3         left         arm
        # 4         bottom       grip
        # 5         right        grip
        # 6         top          grip
        # 7         left         grip

        self.bottomSide = CubeSide.CubeSide(pwmObj=self.pwm,
                                            gripChannel=4, gripForwardDegree=90, gripMiddleDegree=-6, gripBackDegree=-95,
                                            armChannel=0, armInDegree=15, armOutDegree=-80)

        self.rightSide = CubeSide.CubeSide(pwmObj=self.pwm,
                                            gripChannel=5, gripForwardDegree=87, gripMiddleDegree=-5, gripBackDegree=-87,
                                            armChannel=1, armInDegree=10, armOutDegree=-85)

        self.topSide = CubeSide.CubeSide(pwmObj=self.pwm,
                                            gripChannel=6, gripForwardDegree=87, gripMiddleDegree=-4, gripBackDegree=-87,
                                            armChannel=2, armInDegree=15, armOutDegree=-80)

        self.leftSide = CubeSide.CubeSide(pwmObj=self.pwm,
                                            gripChannel=7, gripForwardDegree=87, gripMiddleDegree=-5, gripBackDegree=-87,
                                            armChannel=3, armInDegree=10, armOutDegree=-85)

    def presentTheCube(self):
        print("presentTheCube()")
        self.topSide.arm.setOut()
        self.bottomSide.arm.setOut()
        self.topSide.grip.setForward()
        self.bottomSide.grip.setForward()
        self.bottomSide.arm.setIn()
        self.topSide.arm.setIn()
        self.rightSide.arm.setOut()
        self.leftSide.arm.setOut()
        self.rightSide.grip.setMiddle()
        self.leftSide.grip.setMiddle()


    def holdTheCube(self):
        print("holdTheCube()")
        self.topSide.arm.setOut()
        self.bottomSide.arm.setOut()
        self.topSide.grip.setForward()
        self.bottomSide.grip.setForward()
        self.bottomSide.arm.setIn()
        self.topSide.arm.setIn()
        self.rightSide.arm.setIn()
        self.leftSide.arm.setIn()
        self.rightSide.grip.setMiddle()
        self.leftSide.grip.setMiddle()

    def rMove(self):
        print("rMove()")
        self.rightSide.grip.setForward()

    def lMove(self):
        print("lMove()")
        self.leftSide.grip.setBack()

    def test(self):
        print("test()")
        self.leftSide.arm.setOut()
        self.rightSide.arm.setOut()
        self.bottomSide.arm.setOut()
        self.topSide.arm.setOut()
        self.bottomSide.arm.setIn()
        self.topSide.arm.setIn()

    def uMove(self):
        print("uMove()")
        self.topSide.grip.setMiddle()

    def dMove(self):
        print("dMove()")
        self.bottomSide.grip.setMiddle()


# arm test program
if __name__ == "__main__":



    machine = CubeMachine()

    time.sleep(1)
    machine.presentTheCube()
    input("Press Enter to continue...")
    machine.holdTheCube()
    time.sleep(1)
    machine.uMove()
    machine.dMove()
    machine.rMove()
    machine.lMove()






