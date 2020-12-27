import RPi.GPIO as gpio
import time
from datetime import datetime
import pigpio
import asyncio

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
gpio.setmode(gpio.BCM)

gpio_gates = [5,6,7,8]

# shift register pins
dataPin = 10
clockPin = 11
latchPin = 18

pi = pigpio.pi()

shifter = SegmentShifter(dataPin, clockPin, latchPin)

# setup GPIO
for pin in gpio_gates:
    gpio.setup(pin, gpio.OUT)

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

digits = dict()
digits["0"] = A | B | C | D | E | F
digits["1"] = B | C
digits["2"] = A | B | G | E | D
digits["3"] = A | B | G | C | D
digits["4"] = F | G | B | C
digits["5"] = A | F | G | C | D
digits["6"] = A | F | G | E | D | C
digits["7"] = A | B | C
digits["8"] = A | B | C | D | E | F | G
digits["9"] = A | B | G | F | C | D


currentChar = 0
def nextChar(gpioPin, level, tick):
    global currentChar
    global gpio_gates

    now = datetime.now()
    ctime = now.strftime("%H%M")

    for i in range(len(gpio_gates)):
        if i != currentChar:
            gpio.output(gpio_gates[i], gpio.LOW)

    shifter.setValue(digits[ctime[currentChar]])
    gpio.output(gpio_gates[currentChar], gpio.HIGH)

    currentChar = currentChar + 1

    if currentChar >= 4:
        currentChar = 0

pi.hardware_clock(4, 5000)
cb1 = pi.callback(4, pigpio.RISING_EDGE, nextChar)

while True:
    time.sleep(1)
