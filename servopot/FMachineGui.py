

from tkinter import *
root = Tk()
varSpm = StringVar()

scaleStroke = None



import pigpio
import time
import RPi.GPIO as GPIO
import threading
import random

import pickle
from FMachineConfig import FMachineConfig

config = FMachineConfig()


def saveConfig():
    global config

    with open('FMachine.config', 'wb') as handle:
        pickle.dump(config, handle, protocol=pickle.HIGHEST_PROTOCOL)


def loadConfig():
    global config
    with open('FMachine.config', 'rb') as handle:
        config = pickle.load(handle)



loadConfig()


from datetime import datetime


pi = pigpio.pi()
servopin = 18
relaypin = 27

min = 650
max = 2200

slowSpeed = 950
fastSpeed = 2000

currentSpeed = min
currentSpeedRatio = 0

currentRandomWaitTime = None


relay = True

speedpin = 22
bottompin = 23
middlepin = 24
toppin = 25




GPIO.setmode(GPIO.BCM)
GPIO.setup(speedpin, GPIO.IN)
GPIO.setup(bottompin, GPIO.IN)
GPIO.setup(middlepin, GPIO.IN)
GPIO.setup(toppin, GPIO.IN)


middle_diffs=[None, None, None, None, None, None, None, None, None, None]
middle_last_time = None
avg0, avg1, avg2, avg3 = None, None, None, None

#spm_ratio=[None,None,None,None] #1,4,7,10
spm_rejectCountdown = 5
spm_ratio_startTime = None
spm_ratio_tickCount = 0

learnMode = 0 # 0 no, 1 = wait for down stroke, 2 = found top waiting for middle, 3 recording details waiting for next down stroke, 4 almost done waiting for last middle to stop it
# 5 - speed 1 SPM
# 6 - speed 4 SPM
# 7 - speed 7 SPM
# 8 - speed 10 SPM


#learnTicksLower=None
#learnTicksUpper=None

sideLowerOrUpper = 0 # 0 == upper, 1 == lower
ticks = 0

degrees = 0



databaseOfModes = []

databaseOfModes.append({"name":"Slow 2s Fast 2s",
                        "instructions":[{"action":"do","speed":1},{"action":"wait","time":2.0},{"action":"do","speed":10},{"action":"wait","time":2.0}]})

databaseOfModes.append({"name":"Fast 2 Slow 2",
                        "instructions":[{"action":"do","speed":5},
                                        {"action":"angle","degree":360},{"action":"angle","degree":360},
                                        {"action":"do","speed":1},
                                        {"action":"angle","degree":360},{"action":"angle","degree":360}]})

databaseOfModes.append({"name":"Steady Slow",
                        "instructions":[{"action":"do","speed":1},{"action":"wait","time":2.0}]})

databaseOfModes.append({"name":"Stop",
                        "instructions":[{"action":"do","speed":0},{"action":"wait","time":2.0}]})


databaseOfModes.append({"name":"Steady Fast",
                        "instructions":[{"action":"do","speed":7},{"action":"wait","time":2.0}]})

databaseOfModes.append({"name":"Fast Deep Stop",
                        "instructions":[{"action":"do","speed":5},
                                        {"action":"angle","degree":180-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4}]})

databaseOfModes.append({"name":"Slow Deep Stop",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"angle","degree":180-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4}]})


databaseOfModes.append({"name":"Fast Shallow Stop",
                        "instructions":[{"action":"do","speed":5},
                                        {"action":"angle","degree":360-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4}]})

databaseOfModes.append({"name":"Slow Shallow Stop",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"angle","degree":360-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4}]})




databaseOfModes.append({"name":"Slow Shallow Stop Deep Stop",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"angle","degree":360-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4},
                                        {"action":"do","speed":1},
                                        {"action":"angle","degree":180-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4}]})


databaseOfModes.append({"name":"Fast Shallow Stop Deep Stop",
                        "instructions":[{"action":"do","speed":5},
                                        {"action":"angle","degree":360-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4},
                                        {"action":"do","speed":5},
                                        {"action":"angle","degree":180-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":4}]})



databaseOfModes.append({"name":"Fast 2 Deep Stop",
                        "instructions":[{"action":"do","speed":5},
                                        {"action":"angle","degree":180-30},
                                        {"action":"angle","degree":180-30},
                                        {"action":"do","speed":0},
                                        {"action":"wait","time":2}]})



databaseOfModes.append({"name":"Fast Up Slow Down",
                        "instructions":[{"action":"do","speed":5},
                                        {"action":"angle","degree":360},
                                        {"action":"do","speed":1},
                                        {"action":"angle","degree":180},
                                        {"action":"do","speed":0},
                                        {"action": "wait", "time": 2}]})

databaseOfModes.append({"name":"Slow Up Fast Down",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"angle","degree":360},
                                        {"action":"do","speed":5},
                                        {"action":"angle","degree":180}]})



databaseOfModes.append({"name":"Wave",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"increase", "delta": 0.05, "until":10},
                                        {"action":"decrease", "delta": 0.05, "until": 1},]})


databaseOfModes.append({"name":"Climb",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"increase", "delta": 0.05, "until":10}]})

databaseOfModes.append({"name":"Descend",
                        "instructions":[{"action":"do","speed":10},
                                        {"action":"decrease", "delta": 0.05, "until":1}]})



databaseOfModes.append({"name":"Random Tease",
                        "instructions":[{"action":"do","speed":2},
                                        {"action":"do","speed":4,"chance":0.33},
                                        {"action":"do","speed":6,"chance":0.1},
                                        {"action":"do","speed":10,"chance":0.05},
                                        {"action":"decrease", "delta": 0.1, "until": 1,"chance":0.5},
                                        {"action":"wait","randomLow":0,"randomHigh":4},
                                        {"action":"angle","degree":360-45},
                                        {"action":"angle","degree":180,"chance":0.5},
                                        {"action":"do","speed":0},
                                        {"action":"wait","randomLow":2,"randomHigh":20}
                                        ]})


databaseOfModes.append({"name":"Random Tease Medium",
                        "instructions":[{"action":"do","speed":2},
                                        {"action":"do","speed":4,"chance":0.50},
                                        {"action":"do","speed":6,"chance":0.2},
                                        {"action":"do","speed":10,"chance":0.1},
                                        {"action":"decrease", "delta": 0.1, "until": 1,"chance":1},
                                        {"action":"wait","randomLow":2,"randomHigh":6},
                                        {"action":"angle","degree":360-45},
                                        {"action":"angle","degree":180,"chance":0.5},
                                        {"action":"do","speed":0},
                                        {"action":"wait","randomLow":2,"randomHigh":8}
                                        ]})



databaseOfModes.append({"name":"Random Tease Fast",
                        "instructions":[{"action":"do","speed":4},
                                        {"action":"do","speed":6,"chance":0.50},
                                        {"action":"do","speed":9,"chance":0.2},
                                        {"action":"do","speed":10,"chance":0.1},
                                        {"action":"decrease", "delta": 0.1, "until": 1,"chance":1},
                                        {"action":"wait","randomLow":2,"randomHigh":6},
                                        {"action":"angle","degree":360-45},
                                        {"action":"angle","degree":180,"chance":0.5},
                                        {"action":"do","speed":0},
                                        {"action":"wait","randomLow":3,"randomHigh":15}
                                        ]})




databaseOfModes.append({"name":"Random Tease Fast",
                        "instructions":[{"action":"do","speed":4},
                                        {"action":"do","speed":6,"chance":0.50},
                                        {"action":"do","speed":9,"chance":0.2},
                                        {"action":"do","speed":10,"chance":0.1},
                                        {"action":"decrease", "delta": 0.1, "until": 1,"chance":1},
                                        {"action":"wait","randomLow":2,"randomHigh":6},
                                        {"action":"angle","degree":360-45},
                                        {"action":"angle","degree":180,"chance":0.5},
                                        {"action":"do","speed":0},
                                        {"action":"wait","randomLow":3,"randomHigh":15}
                                        ]})




databaseOfModes.append({"name":"Random Speeds",
                        "instructions":[{"action":"do","speed":4,"randomLow":2,"randomHigh":10},
{"action":"wait", "randomLow":2,"randomHigh":5},
#{"action":"do","speed":2, "randomLow":2,"randomHigh":10},

                                    {"action":"decrease", "delta": 0.1, "until": 1,"chance":1},

                                        {"action":"do","speed":0,"chance":0.5},

{"action":"wait","randomLow":2,"randomHigh":6},
#{"action":"wait","time":2},


                                        {"action": "increase", "delta": 0.1, "until": 9, "chance": 0.25},
{"action":"wait","randomLow":1,"randomHigh":3},
                                        ]})







databaseOfModes.append({"name":"Wave Random",
                        "instructions":[{"action":"do","speed":1},
                                        {"action":"increase", "delta": 0.05,  "until": 2},
                                        {"action":"increase", "delta": 0.05,  "until": 3},
                                        {"action": "increase", "delta": 0.05, "until": 4},
                                        {"action": "increase", "delta": 0.05, "until": 5},
                                        {"action": "do", "speed": 0},
                                        {"action": "do", "speed": 1, "chance":0.5},
                                        {"action":"wait","randomLow":1,"randomHigh":4, "chance":0.5},
                                        {"action":"do","speed":4},
                                        {"action": "increase", "delta": 0.05, "until": 6},
                                        {"action": "increase", "delta": 0.05, "until": 7},
                                        {"action": "increase", "delta": 0.05, "until": 8},
                                        {"action": "do", "speed": 0},
                                        {"action": "do", "speed": 1, "chance":0.5},
                                        {"action": "wait", "randomLow": 1, "randomHigh": 4, "chance": 0.5},
                                        {"action": "do", "speed": 8},
                                        {"action": "increase", "delta": 0.05, "until": 9},
                                        {"action":"increase", "delta": 0.05,  "until": 10},
                                        {"action": "decrease", "delta": 0.05, "until": 9},
                                        {"action": "decrease", "delta": 0.05, "until": 8},
                                        {"action": "decrease", "delta": 0.05, "until": 7},
                                        {"action": "do", "speed": 0},
                                        {"action": "do", "speed": 1, "chance":0.5},
                                        {"action": "wait", "randomLow": 1, "randomHigh": 4, "chance":0.5},
                                        {"action": "do", "speed": 7},
                                        {"action": "decrease", "delta": 0.05, "until": 6},
                                        {"action": "decrease", "delta": 0.05, "until": 5},
                                        {"action": "decrease", "delta": 0.05, "until": 4},
                                        {"action": "decrease", "delta": 0.05, "until": 3},
                                        {"action": "do", "speed": 0},
                                        {"action": "do", "speed": 1, "chance":0.5},
                                        {"action": "wait", "randomLow": 1, "randomHigh": 4, "chance":0.5},
                                        {"action": "do", "speed": 3},
                                        {"action": "decrease", "delta": 0.05, "until": 2},
                                        {"action": "decrease", "delta": 0.05, "until": 1},

                                        ]})





databaseOfModes.append({"name":"Random Speeds 2",
                        "instructions":[{"action": "do", "speed": 5, "randomLow": 2, "randomHigh": 5},
                                        {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 2, "chance":0.2},
                                          {"action":"wait","randomLow":5,"randomHigh":10},
                                          {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 6, "chance":0.50},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":0,"randomHigh":3},
                                         {"action": "increase", "delta": 0.1, "until": 6},
                                         {"action":"wait","randomLow":2,"randomHigh":10},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":10,"randomHigh":15},

                                        {"action":"do","speed":0,"chance":75},

                                        {"action": "do", "skip": 2, "chance":0.7},
                                         {"action":"do","speed":0},
                                         {"action":"wait","randomLow":15,"randomHigh":30},

                                        {"action":"wait","randomLow":1,"randomHigh":6},

                                        {"action": "do", "skip": 5, "chance":0.25},
                                         {"action": "do", "speed":3},
                                         {"action": "angle", "degree": 180 - 30},
                                         {"action": "angle", "degree": 360 - 30},
                                         {"action": "do", "speed":0},
                                         {"action":"wait","randomLow":5,"randomHigh":15},




                                        ]})





databaseOfModes.append({"name":"Random Speeds 3",
                        "instructions":[{"action": "do", "speed": 5, "randomLow": 3, "randomHigh": 8},
                                        {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 2, "chance":0.2},
                                          {"action":"wait","randomLow":5,"randomHigh":15},
                                          {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 6, "chance":0.50},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":0,"randomHigh":3},
                                         {"action": "increase", "delta": 0.1, "until": 10},
                                         {"action":"wait","randomLow":2,"randomHigh":10},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":10,"randomHigh":15},

                                        {"action":"do","speed":0,"chance":75},

                                        {"action": "do", "skip": 2, "chance":0.9},
                                         {"action":"do","speed":0},
                                         {"action":"wait","randomLow":15,"randomHigh":30},

                                        {"action":"wait","randomLow":1,"randomHigh":3},

                                        {"action": "do", "skip": 5, "chance":0.25},
                                         {"action": "do", "speed":3},
                                         {"action": "angle", "degree": 180 - 30},
                                         {"action": "angle", "degree": 360 - 30},
                                         {"action": "do", "speed":0},
                                         {"action":"wait","randomLow":1,"randomHigh":8},




                                        ]})




databaseOfModes.append({"name":"Random Speeds 4",
                        "instructions":[{"action": "do", "speed": 5, "randomLow": 3, "randomHigh": 8},
                                        {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 2, "chance":0.2},
                                          {"action":"wait","randomLow":5,"randomHigh":10},
                                          {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 6, "chance":0.50},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":0,"randomHigh":3},
                                         {"action": "increase", "delta": 0.1, "until": 10},
                                         {"action":"wait","randomLow":2,"randomHigh":10},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":10,"randomHigh":15},

                                        {"action":"do","speed":0,"chance":75},

                                        {"action": "do", "skip": 2, "chance":0.7},
                                         {"action":"do","speed":0},
                                         {"action":"wait","randomLow":15,"randomHigh":30},

                                        {"action":"wait","randomLow":1,"randomHigh":6},

                                        {"action": "do", "skip": 5, "chance":0.25},
                                         {"action": "do", "speed":3},
                                         {"action": "angle", "degree": 180 - 30},
                                         {"action": "angle", "degree": 360 - 30},
                                         {"action": "do", "speed":0},
                                         {"action":"wait","randomLow":5,"randomHigh":15},




                                        ]})


databaseOfModes.append({"name":"Random Speeds 5",
                        "instructions":[{"action": "do", "speed": 5, "randomLow": 2, "randomHigh": 4},
                                        {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 2, "chance":0.1},
                                          {"action":"wait","randomLow":5,"randomHigh":10},
                                          {"action": "angle", "degree": 180 - 30},

                                        {"action": "do", "skip": 4, "chance":0.80},
                                         {"action": "increase", "delta": 0.1, "until": 10},
                                         {"action":"wait","randomLow":2,"randomHigh":10},
                                         {"action": "decrease", "delta": 0.1, "until": 2},
                                         {"action":"wait","randomLow":10,"randomHigh":15},

                                        {"action":"do","speed":0,"chance":75},
                                        {"action":"wait","randomLow":1,"randomHigh":6},
                                        {"action":"wait","randomLow":5,"randomHigh":10,"chance":0.10},
                                        {"action":"wait","randomLow":5,"randomHigh":10,"chance":0.10},
                                        {"action":"wait","randomLow":15,"randomHigh":30,"chance":0.30}
                                        ]})







databaseOfModes.append({"name":"AutoGenerated",
"instructions":[
{"action": "do", "spm":  41.6915600022847 },
{"action": "wait", "time":  7.195701 },
{"action": "do", "spm":  33.48102931398041 },
{"action": "wait", "time":  8.960298 },
{"action": "do", "spm":  26.928763725590873 },
{"action": "wait", "time":  11.140504 },
{"action": "do", "spm":  41.997290334827596 },
{"action": "wait", "time":  7.143318 },
{"action": "do", "spm":  41.24073011488843 },
{"action": "wait", "time":  7.274362 },
{"action": "do", "spm":  41.8048957155974 },
{"action": "wait", "time":  7.176193 },
{"action": "do", "spm":  42.454155879773225 },
{"action": "wait", "time":  7.066446 },
{"action": "do", "spm":  58.476420260676186 },
{"action": "wait", "time":  5.130273 },
{"action": "do", "spm":  57.05156377385445 },
{"action": "wait", "time":  5.258401 },
{"action": "do", "spm":  56.669981230902216 },
{"action": "wait", "time":  5.293808 },
{"action": "do", "spm":  49.61201748592093 },
{"action": "wait", "time":  6.046922 },
{"action": "do", "spm":  9.486366983901318 },
{"action": "wait", "time":  12.649732 },
{"action": "do", "speed": 2},
{"action": "angle", "degree": 180 - 30},
{"action": "do", "speed": 0},
{"action": "wait", "time":  7.515568 },
{"action": "do", "spm":  16.07344492768959 },
{"action": "wait", "time":  18.664325 },
{"action": "do", "spm":  15.714663614529776 },
{"action": "wait", "time":  19.09045 },
{"action": "do", "spm":  23.57003911762259 },
{"action": "wait", "time":  12.728023 },
{"action": "do", "spm":  49.515948591881966 },
{"action": "wait", "time":  6.058654 },
{"action": "do", "spm":  49.756706291801855 },
{"action": "wait", "time":  6.029338 },
{"action": "do", "spm":  44.171685919877575 },
{"action": "wait", "time":  6.791681 },
{"action": "do", "spm":  44.08284754035344 },
{"action": "wait", "time":  6.805368 },
{"action": "do", "spm":  45.053967895443556 },
{"action": "wait", "time":  6.658681 },
{"action": "do", "spm":  43.33777112109613 },
{"action": "wait", "time":  6.922368 },
{"action": "do", "spm":  45.12748740830283 },
{"action": "wait", "time":  6.647833 },
{"action": "do", "spm":  44.00759571101972 },
{"action": "wait", "time":  6.817005 },
{"action": "do", "spm":  44.79778280840287 },
{"action": "wait", "time":  6.69676 },
{"action": "do", "spm":  44.49671985013505 },
{"action": "wait", "time":  6.74207 },
{"action": "do", "spm":  36.88918427561631 },
{"action": "wait", "time":  4.879479 },
{"action": "do", "speed": 0}
]})








def setInstructionsForName(name):
    global instructions, instructionsIndex
    for entry in databaseOfModes:
        if entry["name"]==name:
            instructionsIndex = 0
            instructions =  entry["instructions"]



instructions = [{"action":"do","speed":1},{"action":"wait","time":2.0},{"action":"do","speed":10},{"action":"wait","time":2.0}]
instructionsIndex = 0



from enum import Enum
class Mode(Enum):
    MANUAL = 0
    FAST2SLOW2 = 2
    FASTDOWNSLOWUP = 3
    FASTUPSLOWDOWN = 4

    FASTDEEPSTOP = 5
    SLOWDEEPSTOP = 6

    FASTSHALLOWSTOP = 7
    SLOWSHALLOWSTOP = 8

    SHALLOWSTOPDEEDSTOP = 9
    SHALLOWSTOPDEEDSTOPFAST = 10

    STEADYSLOW = 11
    STEADYFAST = 12
    CLIMB = 13
    DESCEND = 14

    WAVE = 15

    DOUBLEFASTDEEPSTOP = 16

    NEXT = 100

    INSTRUCTIONS = 200

mode = Mode.MANUAL


class ActionReason(Enum):
    UNDEFINED = 0
    SPEED_TICK = 1
    MIDDLE_DOWN_STROKE = 2
    MIDDLE_UP_STROKE = 3
    TOP_DOWN_STROKE = 4
    TOP_UP_STROKE = 5



    TIMER = 99
    START = 100
    NEXT_INSTRUCTION = 101


def clearSpm():
    global middle_diffs, middle_last_time,  avg0, avg1, avg2, avg3

    middle_diffs = [None, None, None, None, None, None, None, None, None, None]
    middle_last_time = None
    avg0, avg1, avg2, avg3 = None, None, None, None

def getDegrees(upperLower, ticks):
    global config

    if config.learnTicksUpper != None and config.learnTicksLower != None:

        if upperLower == 0: # upper
            ratio = ticks / config.learnTicksUpper
            if ratio > 1:
                print("warning more ticks found")
                ratio = 1

            if ratio >= 0.5:
                degrees = 180 * (ratio-0.5) # sine the (ratio-0.5) is no 0 to 0.5 (we get 0 to 90)
            else:
                degrees = 180 * ratio + 270 # since ratio is < 0.5 max is 90+270=360

        else: # lower
            ratio = ticks / config.learnTicksLower
            if ratio > 1:
                print("warning more ticks found")
                ratio = 1

            degrees = 180 * ratio + 90

        return degrees

    else:
        return None


def passThroughDegree(lastDegree, currentDegree, passDegree):
    if lastDegree == None or currentDegree == None or passDegree == None:
        return False
    if passDegree > lastDegree and passDegree <= currentDegree:
        return True
    if lastDegree > currentDegree:
        print ("lastDegree > currentDegree")
        newCurrentDegree = 360+currentDegree

        if passDegree < 180:
            newPassDegree = passDegree+360
        else:
            newPassDegree = passDegree

        if newPassDegree > lastDegree and newPassDegree <= newCurrentDegree:
            return True
    else:
        False

actionCounter =0
actionLastDegree = 0
actionLastStop = None

def startActionMode(m = 0):
    global mode, actionCounter, instructions, instructionsIndex
    mode = m



    if mode == Mode.INSTRUCTIONS:
        instructionsIndex = 0;
        doAction(reason=ActionReason.START)
    elif mode == Mode.FAST2SLOW2:
        actionCounter=0
        doAction(reason=ActionReason.START)
    elif mode == Mode.FASTDOWNSLOWUP or mode == Mode.FASTUPSLOWDOWN:
        actionCounter=0
        doAction(reason=ActionReason.START)

    elif  mode == Mode.FASTDEEPSTOP:
        actionCounter=0
        doAction(reason=ActionReason.START)

    elif  mode == Mode.SLOWDEEPSTOP:
        actionCounter=0
        doAction(reason=ActionReason.START)

    elif  mode == Mode.FASTSHALLOWSTOP:
        actionCounter=0
        doAction(reason=ActionReason.START)

    elif  mode == Mode.SLOWSHALLOWSTOP:
        actionCounter=0
        doAction(reason=ActionReason.START)
    else:
        actionCounter = 0
        doAction(reason=ActionReason.START)


lastInstructionTime = None

def gotoNextInstruction():
    global instructionsIndex, instructions, currentRandomWaitTime
    currentRandomWaitTime = None
    instructionsIndex += 1
    if instructionsIndex >= len(instructions):
        instructionsIndex = 0

    #ins = instructions[instructionsIndex]
    #if ins["action"]=="goto":
    #    instructionsIndex = ins["step"]
    # don't go into an infinite loop if there is only one instruction.
    if len(instructions) > 1:
        doInstruction(reason = ActionReason.NEXT_INSTRUCTION)


def doInstruction(reason=0):
    global instructionsIndex, instructions, lastInstructionTime, actionLastDegree, degrees, currentSpeedRatio
    global currentRandomWaitTime

    if instructions == None:
        print ("ERROR: Instructions == None")
        return

    if instructionsIndex >= len(instructions):
        print ("ERROR: ins >= len(instructions) % >= %".format(instructionsIndex, len(instructions)))
        return

    ins = instructions[instructionsIndex]

    if not ("action" in ins):
        print ("ERROR: action not in instruction %".format(ins))
        return


    if reason == ActionReason.START or reason == ActionReason.NEXT_INSTRUCTION:
        lastInstructionTime = datetime.now()

        if "chance" in ins:
            r = random.uniform(0, 1)
            if r > ins["chance"]:
                gotoNextInstruction()
                return


    if ins["action"]=="do":



        if "servo" in ins:

            if ins["servo"] >= min and ins["servo"]<=max:
                servoToX(ins["servo"])
            else:
                print ("ERROR: servo out of range should be: % <= % <= % (instruction=%)".format(min, ins["servo"], max, ins))
                return
        elif "speed" in ins:

            if ("randomLow" in ins) and ("randomHigh" in ins):
                tempSpeed = random.randint(ins["randomLow"], ins["randomHigh"])
                ins["speed"] = tempSpeed

            if ins["speed"] == 0:
                servoToMin()
            elif ins["speed"] == 1:
                servoToSlow()
            elif ins["speed"] == 10:
                servoToFast()
            elif ins["speed"] > 1 and ins["speed"] < 10:
                ratio = (ins["speed"]-1)/9
                setSpeed = slowSpeed +((fastSpeed-slowSpeed) * ratio)
                servoToX(setSpeed)
            else:
                print ("ERROR: speed out of range 0 or 1.0 to 10.0",ins["speed"])
        elif "spm" in ins:
            servoToSpm(ins["spm"])
        elif "skip" in ins:
            instructionsIndex+=ins["skip"]
            print ("Skipping {} instructions".format(ins["skip"]))

        gotoNextInstruction()


    # we know the mode is instruction
    if reason == ActionReason.START:
        pass
    elif reason == ActionReason.NEXT_INSTRUCTION:
        pass
    elif reason == ActionReason.SPEED_TICK:
        if ins["action"] == "angle":
            if "degree" in ins:
                if passThroughDegree(actionLastDegree, degrees, ins["degree"]):
                    # we passed through the angle

                    # set the dgrees so we dont' hit this during the next instruction
                    actionLastDegree = degrees
                    gotoNextInstruction()
            else:
                print ("ERROR: degree missing (instruction=%)".format(ins))
                return
        elif ins["action"] == "increase":
            currentSpeedRatio = currentSpeedRatio + ins["delta"]
            if currentSpeedRatio >= ins["until"]:
                currentSpeedRatio= ins["until"]
                servoToRatio(currentSpeedRatio)
                gotoNextInstruction()
            else:
                servoToRatio(currentSpeedRatio)

        elif ins["action"] == "decrease":
            currentSpeedRatio = currentSpeedRatio - ins["delta"]
            if currentSpeedRatio <= ins["until"]:
                currentSpeedRatio = ins["until"]
                servoToRatio(currentSpeedRatio)
                gotoNextInstruction()
            else:
                servoToRatio(currentSpeedRatio)

    elif reason == ActionReason.TIMER:
        if ins["action"] == "wait":
            if "time" in ins:
                diff = (datetime.now() - lastInstructionTime).total_seconds()
                # print ("diff:",diff)
                if diff >= ins["time"]:  # pause for x seconds
                    gotoNextInstruction()
            elif ("randomLow" in ins) and ("randomHigh" in ins) :
                if currentRandomWaitTime == None:
                    currentRandomWaitTime = random.randint(ins["randomLow"], ins["randomHigh"])
                    print("currentRandomWaitTime=",currentRandomWaitTime)
                else:
                    diff = (datetime.now() - lastInstructionTime).total_seconds()
                    if diff >= currentRandomWaitTime:  # pause for x seconds
                        currentRandomWaitTime = None
                        gotoNextInstruction()
            else:
                print ("ERROR: time missing (instruction=%)".format(ins))
                return


def doAction(reason=0):

    global mode
    global actionCounter
    global actionLastDegree
    global degrees
    global actionLastStop

    if mode == Mode.MANUAL:
        #print("MANUAL")
        #nothing to do
        pass
    elif mode == Mode.INSTRUCTIONS:
        #print("INSTRUCTIONS")
        doInstruction(reason)


    else:
        print ("unknown mode",mode)



    actionLastDegree = degrees


def speed_callback(channel):
    #print ("speed_callback")
    global config
    global learnMode #, learnTicksLower, learnTicksUpper
    #print ("learnMode = ",learnMode)
    #print("learnTicksLower = ", learnTicksLower)
    #print("learnTicksUpper = ", learnTicksUpper)

    if learnMode == 3:
        config.learnTicksLower+=1
    elif learnMode == 4:
        config.learnTicksUpper += 1

    #print("learnTicksLower = ", learnTicksLower)
    #print("learnTicksUpper = ", learnTicksUpper)


    global ticks
    ticks = ticks + 1


    #print("ticks = ", ticks)
    #print("sideLowerOrUpper = ", sideLowerOrUpper)

    global degrees, scaleStroke

    degrees = getDegrees(sideLowerOrUpper, ticks)

    if degrees != None:
        #print ("degrees:",degrees)
        if degrees > 180:
            scaleStroke.set(180-(degrees-180))
        else:
            scaleStroke.set(degrees)
        #print ("degrees = ", degrees)

    doAction(ActionReason.SPEED_TICK)




def update_middle_times():
    global avg0, avg1, avg2, avg3
    global varSpm
    global middle_diffs
    global middle_last_time
    #global spm_ratio
    global config

    #print ("update_middle_times ", middle_last_time)
    now = datetime.now()
    if middle_last_time != None:
        diff = ((now - middle_last_time).microseconds)/1000000
        #print (diff)
        if diff > 2: # if it's been 2 seconds stop the timer
            middle_diffs = [1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000]
            avg0, avg1, avg2, avg3 = 1, 1, 1, 1
            varSpm.set(str(avg3))
    else:
        #print ("middle_last_time=None")
        pass



    threading.Timer(1, update_middle_times).start()

def getSpmForStartEndTicks (start, end, ticks):
    diff = (end - start).total_seconds()
    print ('diff:',diff)
    avg = (ticks/2)/diff
    print('avg:', avg)
    spm = avg * 60
    print ('spm:',spm)
    return  spm

def middle_callback(channel):
    global middle_last_time
    global middle_diffs
    global avg0, avg1, avg2, avg3
    global varSpm

    global spm_rejectCountdown
    global spm_ratio_startTime
    global spm_ratio_tickCount

    global config

    #print ("middle_callback")

    now = datetime.now()

    if middle_last_time != None:
        diff = (now - middle_last_time).microseconds
        for i in range (len(middle_diffs)-1,0,-1):
            #print (i, " <- ", i-1)
            middle_diffs[i]=middle_diffs[i-1]
        middle_diffs[0]=diff
        #if learnMode>=5 and spm_rejectCountdown==0:
        #    print ("middle_diffs:",middle_diffs)

    middle_last_time = now
    #print (middle_diffs)

    if middle_diffs[0] != None:
        avg0 = middle_diffs[0]
        avg0 = (60 / (avg0 / 1000000))/2 # bpm
    else:
        avg0 = 0

    if middle_diffs[2] != None:
        avg1 = (middle_diffs[0]+middle_diffs[1]+middle_diffs[2])/3
        avg1 = (60 / (avg1 / 1000000))/2 # bpm
    else:
        avg1 = 0

    if middle_diffs[5] != None:
        avg2 = (middle_diffs[0]+middle_diffs[1]+middle_diffs[2]+middle_diffs[3]+middle_diffs[4])/5
        avg2 = (60 / (avg2 / 1000000))/2  # bpm
        varSpm.set(str(int(avg2)))
    else:
        avg2 = 0
        varSpm.set(str(int(avg2)))

    if middle_diffs[9] != None:
        avg3 = (middle_diffs[0]+middle_diffs[1]+middle_diffs[2]+middle_diffs[3]+middle_diffs[4]+middle_diffs[5]+middle_diffs[6]+middle_diffs[7]+middle_diffs[8]+middle_diffs[9])/10
        avg3 = (60 / (avg3 / 1000000))/2 # bpm
        #varSpm.set(str(int(avg3)))

    else:
        avg3 = 0
        #varSpm.set(str(avg3))

    #switch as we go through middle
    global sideLowerOrUpper, ticks
    if sideLowerOrUpper == 1:
        sideLowerOrUpper = 0
        ticks = 0
        doAction(ActionReason.MIDDLE_DOWN_STROKE)
    else:
        sideLowerOrUpper = 1
        ticks = 0
        doAction(ActionReason.MIDDLE_UP_STROKE)


    #print (int(avg0), int(avg1), int(avg2), int(avg3))
    global learnMode#, learnTicksLower, learnTicksUpper


    #print("learnMode = ", learnMode)
    #print("learnTicksLower = ", learnTicksLower)
    #print("learnTicksUpper = ", learnTicksUpper)

    if learnMode == 2:
        learnMode = 3
        config.learnTicksLower = 0
        config.learnTicksUpper = 0
    elif learnMode == 3:
        learnMode = 4
    elif learnMode == 4:
        learnMode = 5
        servoToRatio(1)
        print ("learnMode=5")

        spm_rejectCountdown = 2



    elif learnMode == 5:
        if spm_rejectCountdown > 0:
            print ("skip")
            spm_rejectCountdown = spm_rejectCountdown -1
            if spm_rejectCountdown == 0:
                spm_ratio_startTime = datetime.now()
                spm_ratio_tickCount = 0
        else:
            spm_ratio_tickCount = spm_ratio_tickCount  + 1
            if spm_ratio_tickCount == 10:
                a = getSpmForStartEndTicks(spm_ratio_startTime,datetime.now(),spm_ratio_tickCount)
                print("speed1=", a)
                config.spm_ratio[0] = a

                learnMode = 6
                print("learnMode=6")
                servoToRatio(4)

                spm_rejectCountdown = 2


    elif learnMode == 6:
        if spm_rejectCountdown > 0:
            print("skip")
            spm_rejectCountdown = spm_rejectCountdown - 1
            if spm_rejectCountdown == 0:
                spm_ratio_startTime = datetime.now()
                spm_ratio_tickCount = 0
        else:
            spm_ratio_tickCount = spm_ratio_tickCount + 1
            if spm_ratio_tickCount == 10:
                a = getSpmForStartEndTicks(spm_ratio_startTime, datetime.now(), spm_ratio_tickCount)
                print("speed4=", a)
                config.spm_ratio[1] = a

                learnMode = 7
                print("learnMode=7")
                servoToRatio(7)

                spm_rejectCountdown = 2

    elif learnMode == 7:
        if spm_rejectCountdown > 0:
            print("skip")
            spm_rejectCountdown = spm_rejectCountdown - 1
            if spm_rejectCountdown == 0:
                spm_ratio_startTime = datetime.now()
                spm_ratio_tickCount = 0
        else:
            spm_ratio_tickCount = spm_ratio_tickCount + 1
            if spm_ratio_tickCount == 10:
                a = getSpmForStartEndTicks(spm_ratio_startTime, datetime.now(), spm_ratio_tickCount)
                print("speed7=", a)
                config.spm_ratio[2] = a

                learnMode = 8
                print("learnMode=8")
                servoToRatio(10)

                spm_rejectCountdown = 2

    elif learnMode == 8:
        if spm_rejectCountdown > 0:
            print("skip")
            spm_rejectCountdown = spm_rejectCountdown - 1
            if spm_rejectCountdown == 0:
                spm_ratio_startTime = datetime.now()
                spm_ratio_tickCount = 0
        else:
            spm_ratio_tickCount = spm_ratio_tickCount + 1
            if spm_ratio_tickCount == 10:
                a = getSpmForStartEndTicks(spm_ratio_startTime, datetime.now(), spm_ratio_tickCount)
                print("speed10=", a)
                config.spm_ratio[3] = a

                learnMode = 0
                print("learnMode=0")
                servoToRatio(0)
                print ("!!!!!finished learning!!!!!")
                saveConfig()


    #print("learnTicksLower = ", learnTicksLower)
    #print("learnTicksUpper = ", learnTicksUpper)
    #print ("----")


def top_callback(channel):
    global sideLowerOrUpper
    if sideLowerOrUpper == 1:
        sideLowerOrUpper = 0  # upper
        print("warning had to switch from lower to upper")
    #print("top_callback")

    global learnMode
    #print("learnMode = ", learnMode)

    if learnMode == 1:
        learnMode = 2


    #print("learnMode = ", learnMode)
    #print("learnTicksLower = ", learnTicksLower)
    #print("learnTicksUpper = ", learnTicksUpper)
    #print ("----")


def bottom_callback(channel):
    global sideLowerOrUpper
    if sideLowerOrUpper == 0:
        sideLowerOrUpper = 1  # lower
        print("warning had to switch from upper to lower")
    #print("bottom_callback")


GPIO.add_event_detect(speedpin, GPIO.FALLING, callback=speed_callback, bouncetime=5)

GPIO.add_event_detect(bottompin, GPIO.FALLING, callback=bottom_callback, bouncetime=5)
GPIO.add_event_detect(middlepin, GPIO.FALLING, callback=middle_callback, bouncetime=5)
GPIO.add_event_detect(toppin, GPIO.FALLING, callback=top_callback, bouncetime=5)

#gpioSetPullUpDown(ButtonCenter, PI_PUD_UP);
#gpioSetISRFunc(ButtonCenter, FALLING_EDGE, 1, displayInterrupt);




def relayOff():
    global relay
    print("relay off")
    pi.write(relaypin, 0)
    relay = False

def relayOn():
    global relay
    print("relay on")
    pi.write(relaypin, 1)
    relay = True


def toggleRelay():
    global relay

    if relay:
        relayOff()
    else:
        relayOn()


def servoToRatio(ratio):
    global currentSpeed, currentSpeedRatio


    print("servoToRatio()")
    print ("ratio:", ratio)
    if ratio < 1:
        servoToMin()
        print ("goto min")
    elif ratio >= 1 and ratio <= 10:
        b = ((ratio -1) / 9)
        print ('b:',b)

        x = (1.0 * slowSpeed) + ((fastSpeed-slowSpeed) * (((1.0*ratio) -1.0) / 9.0))

        servoToX(x)
        print ("goto x=",x)
    else:
        print ("ERROR: servoToRatio(",ratio,") Ratio out of range")
    print("--end servoToRatio()--")

def servoToX(x):
    global currentSpeed, currentSpeedRatio
    currentSpeed = x
    currentSpeedRatio =  (((x - slowSpeed) / (fastSpeed - slowSpeed))*9)+1


    print("servo to (",x,")")
    pi.set_servo_pulsewidth(servopin, x)



def servoToMin():
    global currentSpeed, currentSpeedRatio
    currentSpeed = min
    currentSpeedRatio = 0
    print("servo to minimum/stop (",min,")")
    pi.set_servo_pulsewidth(servopin, min)


def servoToLearn():
    global currentSpeed, currentSpeedRatio
    currentSpeed = slowSpeed
    currentSpeedRatio = 1
    print("servo to learn (",slowSpeed,")")
    pi.set_servo_pulsewidth(servopin, slowSpeed)



def servoToSlow():
    global currentSpeed, currentSpeedRatio
    currentSpeed = slowSpeed
    currentSpeedRatio = 1
    print("servo to slow (",slowSpeed,")")
    pi.set_servo_pulsewidth(servopin, slowSpeed)


def servoToFast():
    global currentSpeed, currentSpeedRatio
    currentSpeed = fastSpeed
    currentSpeedRatio = 10
    print("servo to fast (",fastSpeed,")")
    pi.set_servo_pulsewidth(servopin, fastSpeed)


def servoToSpm (spm):
    #global spm_ratio
    global config

    print ("spm_ratio:",config.spm_ratio)

    if config.spm_ratio[0]== None or config.spm_ratio[1]== None or config.spm_ratio[2]== None or config.spm_ratio[3]== None:
        print ("Error: SPM cannot be calculated because spm_ratio[0,1,2,3]=None")
        return
    else:
        if (spm < (config.spm_ratio[0]/4)):
            # if you want 1/4 the mimumin spm, just stop it
            servoToRatio(0)
        elif spm <= config.spm_ratio[0]:
            # if we are more than 1/4 minimum or exactly minimum than just set to minimim
            servoToRatio(1)
        elif config.spm_ratio[0] <= spm and spm < config.spm_ratio[1]:
            a = spm - config.spm_ratio[0]
            b = config.spm_ratio[1] - config.spm_ratio[0]
            ratio = a/b
            c = 4-1
            servoRatio = 1+c*ratio
            servoToRatio(servoRatio)
        elif config.spm_ratio[1] <= spm and spm < config.spm_ratio[2]:
            a = spm - config.spm_ratio[1]
            b = config.spm_ratio[2] - config.spm_ratio[1]
            ratio = a / b
            c = 7 - 4
            servoRatio = 4 + c * ratio
            servoToRatio(servoRatio)
        elif config.spm_ratio[2] <= spm and spm < config.spm_ratio[3]:
            a = spm - config.spm_ratio[2]
            b = config.spm_ratio[3] - config.spm_ratio[2]
            ratio = a / b
            c = 10 - 7
            servoRatio = 7 + c * ratio
            servoToRatio(servoRatio)
        elif config.spm_ratio[3] < spm :
            # ratio above max, just set to maximum
            servoToRatio(10)


def scaleChanged(x):

    global currentSpeed, currentSpeedRatio



    loc = varLocation.get()

    currentSpeed = loc
    currentSpeedRatio = ((loc-slowSpeed) / (fastSpeed-slowSpeed))

    print ("setting location ({})".format(loc))

    pi.set_servo_pulsewidth(servopin, loc)

def scaleChangedSpm(x):


    loc = varLocationSpm.get()

    servoToSpm(loc)


def scaleChangedRatio(x):


    loc = varLocationRatio.get()

    servoToRatio(loc)



def learn():
    global scaleLocation
    global config
    # clear the config and start over
    config = FMachineConfig()

    startActionMode(Mode.MANUAL)

    # start by getting the motor to a slow-ish speed
    servoToMin ()
    time.sleep(2)
    servoToLearn()
    time.sleep(2)
    # count the speed time pulses for full cycle
    global learnMode

    learnMode =1

   # scaleLocation.set(850)


def debug_timer():

    #print ("learnMode:",learnMode)
    #print ("learnTicksLower:",learnTicksLower)
    #print ("learnTicksUpper:",learnTicksUpper)
    #if learnMode == 0:
    #    print ("degrees:", getDegrees(sideLowerOrUpper,ticks))
    threading.Timer(10, debug_timer).start()



def actionTimer():
    doAction(reason=ActionReason.TIMER)
    threading.Timer(0.1, actionTimer).start()

randomSwitcher = False

def randomTimer():
    global randomSwitcher
    if randomSwitcher == True:

        change = random.randint(0, 1)
        if change == 0:


            # switch to a random instruction
            i = int(random.randint(0,len(databaseOfModes)-1))
            setInstructionsForName(databaseOfModes[i]["name"])
            print ("Random Switch to:", databaseOfModes[i]["name"])
            startActionMode(Mode.INSTRUCTIONS)

            #i = int(random.randint(2, 16))

            #if i == 2:
            #    startActionMode(Mode.FAST2SLOW2)
            #elif i == 3:
            #    startActionMode(Mode.FASTDOWNSLOWUP)
            #elif i == 4:
            #    startActionMode(Mode.FASTUPSLOWDOWN)
            #elif i == 5:
            #    startActionMode(Mode.FASTDEEPSTOP)
            #elif i == 6:
            #    startActionMode(Mode.SLOWDEEPSTOP)
            #elif i == 7:
            #    startActionMode(Mode.FASTSHALLOWSTOP)
            #elif i == 8:
            #    startActionMode(Mode.SLOWSHALLOWSTOP)
            #elif i == 9:
            #    startActionMode(Mode.SHALLOWSTOPDEEDSTOP)
            #elif i == 10:
            #    startActionMode(Mode.SHALLOWSTOPDEEDSTOPFAST)
            #elif i == 11:
            #    startActionMode(Mode.STEADYSLOW)
            #elif i == 12:
            #    startActionMode(Mode.STEADYFAST)
            #elif i == 13:
            #    startActionMode(Mode.CLIMB)
            #elif i == 14:
            #    startActionMode(Mode.DESCEND)
            #elif i == 15:
            #    startActionMode(Mode.WAVE)
            #elif i == 16:
            #    startActionMode(Mode.DOUBLEFASTDEEPSTOP)




        threading.Timer(4, randomTimer).start()

def startRandom():
    global randomSwitcher
    randomSwitcher = not randomSwitcher
    if randomSwitcher:
        print ("random enabled")
    else:
        print ("random disabled")
    randomTimer()

def startFast2Slow2():
    global randomSwitcher
    randomSwitcher=False
    #startActionMode(Mode.FAST2SLOW2)
    setInstructionsForName("Fast 2 Slow 2")
    startActionMode(Mode.INSTRUCTIONS)

def startFastDownSlowUp():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.FASTDOWNSLOWUP)
    setInstructionsForName("Slow Up Fast Down")
    startActionMode(Mode.INSTRUCTIONS)

def startFastUpSlowDown():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.FASTUPSLOWDOWN)
    setInstructionsForName("Fast Up Slow Down")
    startActionMode(Mode.INSTRUCTIONS)


def startManual():
    global randomSwitcher
    randomSwitcher = False
    startActionMode(Mode.MANUAL)

def startFastDeepStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.FASTDEEPSTOP)
    setInstructionsForName("Fast Deep Stop")
    startActionMode(Mode.INSTRUCTIONS)

def startSlowDeepStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.SLOWDEEPSTOP)
    setInstructionsForName("Slow Deep Stop")
    startActionMode(Mode.INSTRUCTIONS)

def startFastShallowStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.FASTSHALLOWSTOP)
    setInstructionsForName("Fast Shallow Stop")
    startActionMode(Mode.INSTRUCTIONS)

def startSlowShallowStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.SLOWSHALLOWSTOP)
    setInstructionsForName("Slow Shallow Stop")
    startActionMode(Mode.INSTRUCTIONS)

def startShallowStopDeeoStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.SHALLOWSTOPDEEDSTOP)
    setInstructionsForName("Slow Shallow Stop Deep Stop")
    startActionMode(Mode.INSTRUCTIONS)

def startShallowStopDeeoStopFast():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.SHALLOWSTOPDEEDSTOPFAST)
    setInstructionsForName("Fast Shallow Stop Deep Stop")
    startActionMode(Mode.INSTRUCTIONS)

def startSteadySlow():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.STEADYSLOW)
    setInstructionsForName("Steady Slow")
    startActionMode(Mode.INSTRUCTIONS)

def startSteadyFast():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.STEADYFAST)
    setInstructionsForName("Steady Fast")
    startActionMode(Mode.INSTRUCTIONS)


def startClimb():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.CLIMB)
    setInstructionsForName("Climb")
    startActionMode(Mode.INSTRUCTIONS)

def startDescend():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DESCEND)
    setInstructionsForName("Descend")
    startActionMode(Mode.INSTRUCTIONS)

def startWave():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.WAVE)
    setInstructionsForName("Wave")
    startActionMode(Mode.INSTRUCTIONS)

def startDoubleFastDeepStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Fast 2 Deep Stop")
    startActionMode(Mode.INSTRUCTIONS)


def startRandomTease():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Tease")
    startActionMode(Mode.INSTRUCTIONS)

def startRandomTeaseMedium():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Tease Medium")
    startActionMode(Mode.INSTRUCTIONS)


def startRandomTeaseFast():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Tease Fast")
    startActionMode(Mode.INSTRUCTIONS)

def startAutoGenerated():
    global randomSwitcher
    randomSwitcher = False
    setInstructionsForName("AutoGenerated")
    startActionMode(Mode.INSTRUCTIONS)


def startStop():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Stop")
    startActionMode(Mode.INSTRUCTIONS)



def startWaveRandom():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Wave Random")
    startActionMode(Mode.INSTRUCTIONS)

def startRandomSpeeds():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Speeds")
    startActionMode(Mode.INSTRUCTIONS)

def startRandomSpeeds2():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Speeds 2")
    startActionMode(Mode.INSTRUCTIONS)

def startRandomSpeeds3():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Speeds 3")
    startActionMode(Mode.INSTRUCTIONS)


def startRandomSpeeds4():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Speeds 4")
    startActionMode(Mode.INSTRUCTIONS)

def startRandomSpeeds5():
    global randomSwitcher
    randomSwitcher = False
    #startActionMode(Mode.DOUBLEFASTDEEPSTOP)
    setInstructionsForName("Random Speeds 5")
    startActionMode(Mode.INSTRUCTIONS)



#def startInstructions():
#    startActionMode(Mode.INSTRUCTIONS)


relayOff()
servoToMin()

time.sleep(1)

relayOn()


update_middle_times()

debug_timer()
actionTimer()




root.wm_title("ServoTestGui")

labelTitle = Label(root, text="Servo", font = "Helvetica 16 bold italic")

varLocation = IntVar()
varLocationSpm = IntVar()
varLocationRatio = DoubleVar()

varSpm.set('None')


varLocation.set(min)
varLocationSpm.set(0)
varLocationRatio.set(0)

lblLocation = Label(root, text="Location ")
lblSpm = Label(root, textvariable = varSpm)
btnLearn = Button(root, text="Learn", command=learn)
btnModeManual = Button(root, text="Manual", command=startManual)
btnModeFast2Slow2 = Button(root, text="Fast2 Slow2", command=startFast2Slow2)
btnModeFastDownSlowUp = Button(root, text="Fast Down Slow Up", command=startFastDownSlowUp)
btnModeFastUpSlowDown = Button(root, text="Fast Up Slow Down", command=startFastUpSlowDown)
btnModeFastDeepStop = Button(root, text="Fast Deep Stop", command=startFastDeepStop)
btnModeSlowDeepStop = Button(root, text="Slow Deep Stop", command=startSlowDeepStop)

btnModeFastShallowStop = Button(root, text="Fast Shallow Stop", command=startFastShallowStop)
btnModeSlowShallowStop = Button(root, text="Slow Shallow Stop", command=startSlowShallowStop)

btnModeShallowStopDeeoStop = Button(root, text="Shallow+Deep Stop", command=startShallowStopDeeoStop)
btnModeShallowStopDeeoStopFast = Button(root, text="Shallow+Deep Stop Fast", command=startShallowStopDeeoStopFast)


btnModeSteadySlow = Button(root, text="Slow", command=startSteadySlow)
btnModeSteadyFast = Button(root, text="Fast", command=startSteadyFast)
btnModeClimb = Button(root, text="Climb", command=startClimb)
btnModeDescend = Button(root, text="Descend", command=startDescend)

btnModeWave = Button(root, text="Wave", command=startWave)

btnDoubleFastDeepStop = Button(root, text="2F Deep Stop", command=startDoubleFastDeepStop)
#btnInstructions= Button(root, text="Instructions", command=startInstructions)

btnRandomTease = Button(root, text="Random Tease", command=startRandomTease)
btnRandomTeaseMedium = Button(root, text="Random Tease Medium", command=startRandomTeaseMedium)
btnRandomTeaseFast = Button(root, text="Random Tease Fast", command=startRandomTeaseFast)

btnAutoGenerated= Button(root, text="AutoGenerated", command=startAutoGenerated)


btnModeRandom = Button(root, text="Random", command=startRandom)

btnModeStop = Button(root, text="Stop", command=startStop)

btnModeWaveRandom = Button(root, text="Wave Random", command=startWaveRandom)

btnModeRandomSpeeds = Button(root, text="Random Speeds", command=startRandomSpeeds)
btnModeRandomSpeeds2 = Button(root, text="Random Speeds 2", command=startRandomSpeeds2)
btnModeRandomSpeeds3 = Button(root, text="Random Speeds 3", command=startRandomSpeeds3)
btnModeRandomSpeeds4 = Button(root, text="Random Speeds 4", command=startRandomSpeeds4)
btnModeRandomSpeeds5 = Button(root, text="Random Speeds 5", command=startRandomSpeeds5)

scaleLocation = Scale(root, from_=min, to=max, resolution=25, tickinterval=200, orient=HORIZONTAL, command=scaleChanged, var=varLocation, length=800)

scaleSpm = Scale(root, from_=0, to=200, resolution=2, tickinterval=10, orient=HORIZONTAL, command=scaleChangedSpm, var=varLocationSpm, length=800)

scaleRatio = Scale(root, from_=0, to=10, resolution=0.1, tickinterval=1, orient=HORIZONTAL, command=scaleChangedRatio, var=varLocationRatio, length=800)



scaleStroke = Scale(root, from_=0, to=180, resolution=1, tickinterval=45, orient=VERTICAL, length=200)



lblLocation.grid(row=0,column=0, columnspan=2)
scaleLocation.grid(row=1,column=0, columnspan=6)
scaleSpm.grid(row=2,column=0, columnspan=6)
scaleRatio.grid(row=3,column=0, columnspan=6)



lblSpm.grid(row=4,column=0)



btnLearn.grid(row=4,column=1)
btnModeManual.grid(row=4,column=2)
btnModeFast2Slow2.grid(row=4,column=3)
btnModeFastDownSlowUp.grid(row=4,column=4)
btnModeFastUpSlowDown.grid(row=4,column=5)
btnModeFastDeepStop.grid(row=5,column=0)
btnModeSlowDeepStop.grid(row=5,column=1)
btnModeRandom.grid(row=5,column=2)
btnModeFastShallowStop.grid(row=5,column=3)
btnModeSlowShallowStop.grid(row=5,column=4)
btnModeShallowStopDeeoStop.grid(row=5,column=5)
btnModeShallowStopDeeoStopFast.grid(row=6,column=0)

btnModeSteadySlow.grid(row=6,column=1)
btnModeSteadyFast.grid(row=6,column=2)
btnModeClimb.grid(row=6,column=3)
btnModeDescend.grid(row=6,column=4)
btnModeWave.grid(row=6,column=5)
btnDoubleFastDeepStop.grid(row=7,column=0)

btnRandomTease.grid(row=7,column=1)
btnRandomTeaseMedium.grid(row=7,column=2)
btnRandomTeaseFast.grid(row=7,column=3)

btnAutoGenerated.grid(row=7,column=5)
btnModeStop.grid(row=7,column=4)


btnModeRandomSpeeds.grid(row=8,column=0)
btnModeWaveRandom.grid(row=8,column=1)
btnModeRandomSpeeds2.grid(row=8,column=2)
btnModeRandomSpeeds3.grid(row=8,column=3)
btnModeRandomSpeeds4.grid(row=8,column=4)
btnModeRandomSpeeds5.grid(row=8,column=5)

#btnInstructions.grid(row=4,column=5)


scaleStroke.grid(row=0,column=9, rowspan=10)
root.mainloop()
