
import serial
import time
import RPi.GPIO as GPIO
import asyncio
import threading
from trial import Trial
from datetime import datetime
import pygame

valve_pin = 23
IR_pin = 25
lick_pin = 24
LED_PIN = 17
tdt_pin = 27  # GPIO pin for PWM output

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_pin, GPIO.IN)
GPIO.setup(lick_pin, GPIO.IN)
GPIO.setup(valve_pin, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(tdt_pin, GPIO.OUT)

Fs = 44000  # PWM frequency
pwm = GPIO.PWM(tdt_pin, Fs)  # Set PWM frequency

GPIO.setwarnings(False)

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                    timeout=0.01)  # timeout=1  # Change '/dev/ttyS0' to the detected port



try:
    # Start PWM
    pwm.start(50)  # Start PWM with 50% duty cycle


    time.sleep(2)
finally:
    # Clean up GPIO
    pwm.stop()

    time.sleep(2) # time with no stimulus- that the mouse still can lick
    print('output stoping')
