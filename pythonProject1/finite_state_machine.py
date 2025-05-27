import serial
import time
import RPi.GPIO as GPIO
import asyncio
import threading
from trial import Trial
from datetime import datetime
import numpy as np
import sounddevice as sd

valve_pin = 23
IR_pin = 25
lick_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_pin, GPIO.IN)
GPIO.setup(lick_pin, GPIO.IN)
GPIO.setup(valve_pin, GPIO.OUT)

GPIO.setwarnings(False)

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600,
                    timeout=0.01)  # timeout=1  # Change '/dev/ttyS0' to the detected port

class State:
    def __init__(self, name, fsm):
        self.name = name
        self.fsm = fsm
        self.fsm.exp.live_w.deactivate_states_indicators(name)

    def on_event(self, event):
        pass

class IdleState(State):
    def __init__(self, fsm):
        super().__init__("Idle", fsm)
        ser.flushInput()  # clear the data from the serial
        self.fsm.current_trial.clear_trial()
        self.fsm.exp.live_w.update_last_rfid('')
        self.fsm.exp.live_w.update_level('')
        self.fsm.exp.live_w.update_score('')
        self.fsm.exp.live_w.update_trial_value('')
        self.wait_for_event()

    def wait_for_event(self):
        
        while ser.in_waiting <= 0 or self.fsm.exp.live_w.pause:
            ser.flushInput()  # Flush input buffer
            time.sleep(0.05)
        mouse_id = ser.readline().decode('utf-8').rstrip()  # Read the data from the serial port
        if self.recognize_mouse(mouse_id):
            self.fsm.current_trial.update_current_mouse(self.fsm.exp.mice_dict[mouse_id])
            print("mouse: "+self.fsm.exp.mice_dict[mouse_id].get_id())
            print("Level: "+self.fsm.exp.mice_dict[mouse_id].get_level())
            self.fsm.exp.live_w.update_last_rfid(mouse_id)
            self.fsm.exp.live_w.update_level(self.fsm.exp.mice_dict[mouse_id].get_level())
#             self.fsm.live_w.update_score('')
            self.on_event('in_port')

    def on_event(self, event):
        if event == 'in_port':
            print("Transitioning from Idle to in_port")
            self.fsm.state = InPortState(self.fsm)

    def recognize_mouse(self,data: str):
        if data in self.fsm.exp.mice_dict:
            print('recognized mouse: ' + data)
            return "pass to next state"
        else:
            print("mouse ID: '" +data+ "' does not exist in the mouse dictionary.")
            self.wait_for_event()


class InPortState(State):
    def __init__(self, fsm):
        super().__init__("port", fsm)
        self.wait_for_event()

    def wait_for_event(self):
        while GPIO.input(IR_pin) != GPIO.HIGH: # Waiting for IR rays to break
            time.sleep(0.09)
        self.fsm.exp.live_w.toggle_indicator("IR","on")
        time.sleep(0.1)
        self.fsm.exp.live_w.toggle_indicator("IR","off")
        print("The mouse entered!")
        if self.fsm.exp.exp_params["start_trial_time"] is not None:
            time.sleep(int(self.fsm.exp.exp_params["start_trial_time"]))
            print("sleep before start trial")
        self.on_event('IR_stim')

    def on_event(self, event):
        if event == 'IR_stim':
            print("Transitioning from in_port to trial")
            self.fsm.state = TrialState(self.fsm)


class TrialState(State):
    def __init__(self, fsm):
        super().__init__("trial", fsm)
        self.got_response = None
        self.fsm.current_trial.start_time = datetime.now().strftime('%H:%M:%S')  # Get current time
        self.fsm.current_trial.calculate_stim()
        self.fsm.exp.live_w.update_trial_value(self.fsm.current_trial.current_value)
        self.stop_threads = False
        stim_thread = threading.Thread(target=self.tdt_as_stim)
        input_thread = threading.Thread(target=self.receive_input, args=(lambda: self.stop_threads,))
        stim_thread.start()
        input_thread.start()
        stim_thread.join()
        self.stop_threads = True
        input_thread.join()
        self.fsm.current_trial.score = self.evaluate_response()
        print("score: "+self.fsm.current_trial.score)
        self.fsm.exp.live_w.update_score(self.fsm.current_trial.score)
        if self.fsm.current_trial.score == 'hit':
            self.give_reward()
        elif self.fsm.current_trial.score == 'fa':
            self.give_punishment()
        self.on_event('trial_over')
        
    def give_reward(self):
        GPIO.output(valve_pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(valve_pin, GPIO.LOW)
        
    def give_punishment(self):

        try:
            noise = np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npy')  
            sd.play(noise,len(noise))
            sd.wait()
 
                
        finally:
            self.fsm.exp.live_w.toggle_indicator("stim","off")
            time.sleep(2) # time with no stimulus- that the mouse still can lick
            print('output stoping')

        
    def valve_as_stim(self):
        GPIO.output(valve_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(valve_pin, GPIO.LOW)
        #time.sleep(5)

    def tdt_as_stim(self):
        stim_path = self.fsm.current_trial.current_stim_path
        print(stim_path)
        try:
            tone_shape = np.load(stim_path)
            sd.play(tone_shape,len(tone_shape))
            sd.wait()
            

        finally:
            self.fsm.exp.live_w.toggle_indicator("stim","off")
            #time.sleep(2) # time with no stimulus- that the mouse still can lick
            time.sleep(int(self.fsm.exp.exp_params["time_to_lick_after_stim"]))# time with no stimulus- that the mouse still can lick
            print('output stoping')

    def receive_input(self, stop):
        # when to start counting the licks
        if self.fsm.exp.exp_params["lick_time_bin_size"] != None: # if the user choose "by time"
            time.sleep(int(self.fsm.exp.exp_params["lick_time_bin_size"]))
        elif self.fsm.exp.exp_params["lick_time"] == "1": # "with stim"
            pass
        elif self.fsm.exp.exp_params["lick_time"] == "2": # "after stim"
            time.sleep(int(self.fsm.exp.exp_params["stimulus_length"]))
    
        counter = 0
        print('waiting for licks..')
        self.got_response = False
        while not stop():
            if GPIO.input(lick_pin) == GPIO.HIGH:
                self.fsm.exp.live_w.toggle_indicator("lick","on")
                self.fsm.current_trial.add_lick_time()
                counter += 1
                time.sleep(0.08) ### maybe this if problematic- mayby the mouse licking is very fast
                self.fsm.exp.live_w.toggle_indicator("lick","off")
                print(f"Received input: lick!")
            time.sleep(0.08)
        if counter >= int(self.fsm.exp.exp_params["lick_threshold"]):
            self.got_response = True
            print('threshold has been reached!')
            
        else:
            print('no response received')
        print('input thread stopping')
        print('num of licks: ' + str(counter))

    def on_event(self, event):
        if event == 'trial_over':
            time.sleep(0.5) # wait for showing the score on the live window before it is pass to the next trial
            self.fsm.current_trial.write_trial_to_csv(self.fsm.exp.txt_file_path)
            if self.fsm.exp.exp_params['ITI_time'] == None:
                while GPIO.input(IR_pin) == GPIO.HIGH: # Waiting for IR rays to not break
                    time.sleep(0.09)
#                 while ser.in_waiting > 0: # wait until the mouse exit the port
#                     ser.flushInput()  # Flush input buffer
#                     time.sleep(0.05)
            else:
                time.sleep(int(self.fsm.exp.exp_params['ITI_time']))
            print("Transitioning from trial to idel")
            self.fsm.state = IdleState(self.fsm)
            
    def evaluate_response(self):
        value = self.fsm.current_trial.current_value
        if value == 'go':
            if self.got_response == True:
                return 'hit'
            elif self.got_response == False:
                return 'miss'
        if value == 'no-go':
            if self.got_response == True:
                return 'fa'
            elif self.got_response == False:
                return 'cr'
        if value == 'catch':
            if self.got_response == True:
                return 'catch - response'
            elif self.got_response == False:
                return 'catch - no response'

class FiniteStateMachine:


    def __init__(self,experiment):
        self.exp = experiment
        self.current_trial = Trial(self)
        self.state = IdleState(self)

    def on_event(self, event):
        self.state.on_event(event)

    def get_state(self):
        return self.state.name


if __name__ == "__main__":
    fsm = FiniteStateMachine()


