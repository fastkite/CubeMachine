

from tkinter import *
# Import the PCA9685 module.
import Adafruit_PCA9685


def scaleChanged(x):

    loc = varLocation.get()
    #t = varTilt.get()
    #z = varZoom.get()

    print ("setting location ({})".format(loc))
    pwm.set_pwm(0, 0, loc)


def scaleLimitChanged(x):
    loc = varLocationLimit.get()
    #t = varTilt.get()
    #z = varZoom.get()

    print ("setting location ({})".format(loc))
    pwm.set_pwm(0, 0, loc)






pwm = Adafruit_PCA9685.PCA9685()

# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)




root = Tk()

root.wm_title("ServoTestGui")

labelTitle = Label(root, text="Servo", font = "Helvetica 16 bold italic")

varLocation = IntVar()
varLocationLimit = IntVar()

min = 150
max = 675

varLocation.set(400)


lblLocation = Label(root, text="Location (12 bit)")
lblLocationLimit = Label(root, text="Location (Limit)")



scaleLocation = Scale(root, from_=0, to=4095, resolution=1, tickinterval=200, orient=HORIZONTAL, command=scaleChanged, var=varLocation, length=1000)
scaleLocationLimit = Scale(root, from_=min, to=max, resolution=1, tickinterval=50, orient=HORIZONTAL, command=scaleLimitChanged, var=varLocationLimit, length=1000)


#scaleTilt = Scale(root, from_=0, to=100, orient=VERTICAL, command=scaleChanged, var=varTilt)
#scaleZoom = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=scaleChanged, var=varZoom)



lblLocation.grid(row=0,column=0)
scaleLocation.grid(row=0, column=1)

lblLocationLimit.grid(row=1,column=0)
scaleLocationLimit.grid(row=1, column=1)



lblLocation.grid(row=0,column=0)
scaleLocation.grid(row=0, column=1)


root.mainloop()
