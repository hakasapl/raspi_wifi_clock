import RPi.GPIO as gpio
import time
from datetime import datetime

class SegmentShifter():

    def __init__(self, dataPin, clockPin, latchPin):
        self.clockPin = clockPin
        self.latchPin = latchPin
        self.dataPin = dataPin
    
        gpio.setup(self.clockPin, gpio.OUT)
        gpio.setup(self.latchPin, gpio.OUT)
        gpio.setup(self.dataPin, gpio.OUT)

        gpio.output(self.clockPin, gpio.LOW)
        gpio.output(self.latchPin, gpio.HIGH)
        gpio.output(self.dataPin, gpio.LOW)

        self.registerLength = 16

    def tick(self):
        gpio.output(self.clockPin, gpio.HIGH)
        gpio.output(self.clockPin, gpio.LOW)

    def setValue(self, value):
        gpio.output(self.latchPin, gpio.LOW)

        for i in range(self.registerLength):
            if value % 2 == 0:
                # Low
                gpio.output(self.dataPin, gpio.LOW)
            elif value % 2 == 1:
                # High
                gpio.output(self.dataPin, gpio.HIGH)
            else:
                print("Invalid 2-state bit given")

            self.tick()
            value = value >> 1

        gpio.output(self.latchPin, gpio.HIGH)

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)

q1_gate = 7
q2_gate = 29
q3_gate = 31
q4_gate = 26
q5_gate = 24

# shift register pins
dataPin = 19
clockPin = 23
latchPin = 12

shifter = SegmentShifter(dataPin, clockPin, latchPin)

gpio.setup(q1_gate, gpio.OUT)
gpio.setup(q2_gate, gpio.OUT)
gpio.setup(q3_gate, gpio.OUT)
gpio.setup(q4_gate, gpio.OUT)
gpio.setup(q5_gate, gpio.OUT)

# decimal output is always on
gpio.output(q1_gate, gpio.HIGH)

D3D4 = 0b1000000000000000
D1 = 0b0100000000000000
D2 = 0b0010000000000000
D5 = 0b0001000000000000
F = 0b0000100000000000
G = 0b0000010000000000
A = 0b0000001000000000
B = 0b0000000100000000
C = 0b0000000010000000
D = 0b0000000001000000
E = 0b0000000000100000

digit0 = A | B | C | D | E | F
digit1 = B | C
digit2 = A | B | G | E | D
digit3 = A | B | G | C | D
digit4 = F | G | B | C
digit5 = A | F | G | C | D
digit6 = A | F | G | E | D | C
digit7 = A | B | C
digit8 = A | B | C | D | E | F | G
digit9 = A | B | G | F | C | D

def getStream(number):
    if number == 0:
        return digit0
    elif number == 1:
        return digit1
    elif number == 2:
        return digit2
    elif number == 3:
        return digit3
    elif number == 4:
        return digit4
    elif number == 5:
        return digit5
    elif number == 6:
        return digit6
    elif number == 7:
        return digit7
    elif number == 8:
        return digit8
    elif number == 9:
        return digit9

def stopDrains():
    gpio.output(q2_gate, gpio.LOW)
    gpio.output(q3_gate, gpio.LOW)
    gpio.output(q4_gate, gpio.LOW)
    gpio.output(q5_gate, gpio.LOW)

while True:
    # get current time
    now = datetime.now()
    ctime = now.strftime("%H%M")
    
    for i in range(len(ctime)):
        stopDrains()
        shifter.setValue(getStream(int(ctime[i])))
        if i == 0:
            # First hour digit
            gpio.output(q2_gate, gpio.HIGH)
        elif i == 1:
            # Second hour digit
            gpio.output(q3_gate, gpio.HIGH)
        elif i == 2:
            # Third hour digit
            gpio.output(q4_gate, gpio.HIGH)
        elif i == 3:
            # Fourth hour digit
            gpio.output(q5_gate, gpio.HIGH)
        
        timer = time.time()
        while time.time() <= timer + 0.001:
            continue
