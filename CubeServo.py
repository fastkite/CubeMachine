

class CubeServo(object):
    def __init__(self,
                 pwmObj, # pwm object to control all servos
                 channel, # pwm channel this servo is on
                 frequency=60,  # hertz
                 minExtremePulse=0.6,
                 maxExtremePulse=2.4,

                 minNormalPulse=1.0, # 1.0 millisecond pulse
                 maxNormalPulse=2.0, # 2.0 millisecond pulse

                 normalDegrees=180, # normal 180 degree servo
                ):

        # object to control pwm
        self.pwm = pwmObj

        # frequency of the pwm
        self.frequency=frequency

        # channel of the servo
        self.channel = channel

        self.minExtremePulse = minExtremePulse
        self.maxExtremePulse = maxExtremePulse

        self.minNormalPulse = minNormalPulse
        self.maxNormalPulse = maxNormalPulse

        self.normalDegrees = normalDegrees

        self.currentValue = None


    def setValue(self, value, force=False):
        if not force and value < self.getValueForPulse(self.minExtremePulse):
            print ("Error: value ({}) < self.minExtremePulse ({})".format(value, self.minExtremePulse))
            return False
        if not force and value > self.getValueForPulse(self.maxExtremePulse):
            print ("Error: value ({}) < self.maxExtremePulse ({})".format(value, self.maxExtremePulse))
            return False
        self.pwm.set_pwm(self.channel, 0, value)
        self.currentValue = value # recall where the motor is at
        return True

    def getValueForPulse(self, pulseMs): # pulseMs is the length of the pulse in milliseconds (typically 1 to 2 is permitted, with 1.5 as the middle)
        pulse_length = 1000000  # 1,000,000 us per second
        pulse_length //= self.frequency  # 60 Hz
        print('{0}us per period'.format(pulse_length))
        pulse_length //= 4096  # 12 bits of resolution
        print('{0}us per bit'.format(pulse_length))
        pulseMs *= 1000
        pulseMs //= pulse_length
        return int(pulseMs) # returned value in 12 bit for pwm usage

    def setPulse(self, pulse):
        value = self.getValueForPulse(pulse)
        #print ('pulse({}) = value({})'.format(pulse, value))
        return self.setValue(value)

    def getPulseForDegrees(self, degree): # degree here is -90 to +90 for example, 0 is the middle value

        # convert degrees to 0 to 180 (or 0 to 270) etc...
        degreesNormal = degree + self.normalDegrees/2

        pulseOffset = (self.maxNormalPulse - self.minNormalPulse) * (degreesNormal/self.normalDegrees)

        pulse = self.minNormalPulse + pulseOffset

        return pulse

    def getValueForDegrees(self, degree):
        pulse = self.getPulseForDegrees(degree)
        value = self.getValueForPulse(pulse)
        return value

    def setDegree(self, degree):
        value = self.getValueForDegrees(degree)
        return self.setValue(value)

# SERVO TEST PROGRAM
if __name__ == "__main__":

    from tkinter import *
    # Import the PCA9685 module.
    import Adafruit_PCA9685


    def scaleChanged(x):
        loc = varLocation.get()
        # t = varTilt.get()
        # z = varZoom.get()

        print("setting location ({})".format(loc))
        servo.setValue(loc, force=True)


    def scaleLimitChanged(x):
        loc = varLocationLimit.get()
        # t = varTilt.get()
        # z = varZoom.get()

        print("setting location ({})".format(loc))
        servo.setValue(loc)


    def scaleDegreeChanged(x):
        deg = varDegree.get()
        # t = varTilt.get()
        # z = varZoom.get()

        print("setting degree ({})".format(deg))
        servo.setDegree(deg)


    pwm = Adafruit_PCA9685.PCA9685()
    # Set frequency to 60hz, good for servos.
    pwm.set_pwm_freq(55) # WIERD!!! setting freq to 55 makes the actual frequency 60 hertz!


    # Servo used for inserting and removing arm
    servoArm = CubeServo(pwmObj = pwm, channel=0, frequency=60,
                        normalDegrees = 180,
                        minNormalPulse = 0.6,
                        maxNormalPulse = 2.4,
                        minExtremePulse = 0.5,
                        maxExtremePulse = 2.5)

    # Servo used for gripper
    servoGrip = CubeServo(pwmObj = pwm, channel=4, frequency=60,
                        normalDegrees=270,
                        minNormalPulse = 0.5,
                        maxNormalPulse = 2.5,
                        minExtremePulse=0.4,
                        maxExtremePulse=2.5)

    #servo = servoGrip # lets work with the Grip
    servo = servoArm # lets work with the arm

    servo.setDegree(0)

    print ("0.6ms exMin = {}".format(servo.getValueForPulse(0.6)))
    print ("1ms     min = {}".format(servo.getValueForPulse(1)))
    print ("1.5ms   mid = {}".format(servo.getValueForPulse(1.5)))
    print ("2ms     max = {}".format(servo.getValueForPulse(2)))
    print ("2.4ms exMax = {}".format(servo.getValueForPulse(2.4)))

    root = Tk()

    root.wm_title("ServoTestGui")

    labelTitle = Label(root, text="Servo", font="Helvetica 16 bold italic")

    varLocation = IntVar()
    varLocationLimit = IntVar()

    varDegree = DoubleVar()

    varLocation.set(400)

    lblLocation = Label(root, text="Location (12 bit)")
    lblLocationLimit = Label(root, text="Location (Limit)")
    lblDegree = Label(root, text="Degree")

    scaleLocation = Scale(root, from_=0, to=4095, resolution=1, tickinterval=200, orient=HORIZONTAL,
                               command=scaleChanged, var=varLocation, length=1000)

    min = 150
    max = 600

    scaleLocationLimit = Scale(root, from_=min, to=max, resolution=1, tickinterval=50, orient=HORIZONTAL,
                               command=scaleLimitChanged, var=varLocationLimit, length=1000)


    scaleDegree = Scale(root, from_=-(270/2), to=(270/2), resolution=0.5, tickinterval=10, orient=HORIZONTAL,
                               command=scaleDegreeChanged, var=varDegree, length=1000)



    lblLocation.grid(row=0, column=0)
    scaleLocation.grid(row=0, column=1)

    lblLocationLimit.grid(row=1, column=0)
    scaleLocationLimit.grid(row=1, column=1)



    lblDegree.grid(row=2, column=0)
    scaleDegree.grid(row=2, column=1)

    root.mainloop()