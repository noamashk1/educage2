import serial
import time
import RPi.GPIO as GPIO
import asyncio
import threading

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

Fs = 4400  # PWM frequency
pwm = GPIO.PWM(tdt_pin, Fs)  # Set PWM frequency

GPIO.setwarnings(False)

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                    timeout=0.01)  # timeout=1  # Change '/dev/ttyS0' to the detected port


class State:
    def __init__(self, name, fsm):
        self.name = name
        self.fsm = fsm

    def on_event(self, event):
        pass


class IdleState(State):
    def __init__(self, fsm):
        super().__init__("Idle", fsm)
        ser.flushInput()  # clear the data from the serial
        self.wait_for_event()

    def wait_for_event(self):
        while ser.in_waiting <= 0:
            ser.flushInput()  # Flush input buffer
            time.sleep(0.05)
        data = ser.readline().decode('utf-8').rstrip()  # Read the data from the serial port
        print('recognized mouse: ' + data)
        self.on_event('in_port')

    def on_event(self, event):
        if event == 'in_port':
            print("Transitioning from Idle to in_port")
            self.fsm.state = InPortState(self.fsm)


class InPortState(State):
    def __init__(self, fsm):
        super().__init__("port", fsm)
        self.wait_for_event()

    def wait_for_event(self):
        while GPIO.input(IR_pin) != GPIO.HIGH:
            time.sleep(0.09)
        print("The mouse entered!")
        self.on_event('IR_stim')

    def on_event(self, event):
        if event == 'IR_stim':
            print("Transitioning from in_port to trial")
            self.fsm.state = TrialState(self.fsm)


class TrialState(State):
    def __init__(self, fsm):
        super().__init__("trial", fsm)
        print("trial_constructor")
        self.stop_threads = False
        # stim_thread = threading.Thread(target = self.valve_as_stim)
        stim_thread = threading.Thread(target=self.tdt_as_stim)
        input_thread = threading.Thread(target=self.receive_input, args=(lambda: self.stop_threads,))
        stim_thread.start()
        input_thread.start()
        stim_thread.join()
        self.stop_threads = True
        input_thread.join()
        self.on_event('trial_over')

    def valve_as_stim(self):
        GPIO.output(valve_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(valve_pin, GPIO.LOW)
        time.sleep(3)

    def tdt_as_stim(self):
        try:
            # Start PWM
            pwm.start(50)  # Start PWM with 50% duty cycle

            # Let the PWM signal play for 2 seconds
            time.sleep(0.3)

        finally:
            # Clean up GPIO
            pwm.stop()
            time.sleep(3)

    def receive_input(self, stop):
        counter = 0
        print('wating for licks..')
        while not stop():
            #             print('wating for licks..')
            if GPIO.input(lick_pin) == GPIO.HIGH:
                counter += 1
                print(f"Received input: lick!")

            time.sleep(0.08)
        print('input thread stoping')
        print('num of licks: ' + str(counter))

    def on_event(self, event):
        if event == 'trial_over':
            print("Transitioning from trial to idel")
            self.fsm.state = IdleState(self.fsm)


class FiniteStateMachine:
    def __init__(self):
        self.state = IdleState(self)

    def on_event(self, event):
        self.state.on_event(event)

    def get_state(self):
        return self.state.name


if __name__ == "__main__":
    fsm = FiniteStateMachine()


