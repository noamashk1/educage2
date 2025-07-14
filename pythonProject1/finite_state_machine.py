import serial
import time
import RPi.GPIO as GPIO
import threading
from trial import Trial
from datetime import datetime
import numpy as np
import sounddevice as sd

valve_pin = 4#23
IR_pin = 22#25
lick_pin = 17#24

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

        threading.Thread(target=self.wait_for_event, daemon=True).start()
        
    def wait_for_event(self):
        minutes_passed = 0
        last_log_time = time.time()

        while True:
            
            if time.time() - last_log_time > 60:
                minutes_passed += 1
                last_log_time = time.time()
                print(f"[IdleState] Waiting for RFID... {minutes_passed} minutes passed")

            if ser.in_waiting > 0 and not self.fsm.exp.live_w.pause:
                try:
                    mouse_id = ser.readline().decode('utf-8').rstrip()
                except Exception as e:
                    print(f"[IdleState] Error reading RFID: {e}")
                    continue

                if self.recognize_mouse(mouse_id):
                    self.fsm.current_trial.update_current_mouse(self.fsm.exp.mice_dict[mouse_id])
                    print("mouse: " + self.fsm.exp.mice_dict[mouse_id].get_id())
                    print("Level: " + self.fsm.exp.mice_dict[mouse_id].get_level())
                    self.fsm.exp.live_w.update_last_rfid(mouse_id)
                    self.fsm.exp.live_w.update_level(self.fsm.exp.mice_dict[mouse_id].get_level())
                    self.on_event('in_port')
                    break  
            else:
                ser.flushInput()
                time.sleep(0.05)

#     def wait_for_event(self):
#         while True:
#             if ser.in_waiting > 0 and not self.fsm.exp.live_w.pause:
#                 mouse_id = ser.readline().decode('utf-8').rstrip()
#                 if self.recognize_mouse(mouse_id):
#                     self.fsm.current_trial.update_current_mouse(self.fsm.exp.mice_dict[mouse_id])
#                     print("mouse: " + self.fsm.exp.mice_dict[mouse_id].get_id())
#                     print("Level: " + self.fsm.exp.mice_dict[mouse_id].get_level())
#                     self.fsm.exp.live_w.update_last_rfid(mouse_id)
#                     self.fsm.exp.live_w.update_level(self.fsm.exp.mice_dict[mouse_id].get_level())
#                     self.on_event('in_port')
#                     break
#             else:
#                 ser.flushInput()  # Flush input buffer
#                 time.sleep(0.05)

    def on_event(self, event):
        if event == 'in_port':
            print("Transitioning from Idle to in_port")
            self.fsm.state = InPortState(self.fsm)

    def recognize_mouse(self, data: str):
        if data in self.fsm.exp.mice_dict:
            print('recognized mouse: ' + data)
            return True
        else:
            print("mouse ID: '" + data + "' does not exist in the mouse dictionary.")
            return False


# class InPortState(State):
#     def __init__(self, fsm):
#         super().__init__("port", fsm)
#         threading.Thread(target=self.wait_for_event, daemon=True).start()
# 
#     def wait_for_event(self):
#         while GPIO.input(IR_pin) != GPIO.HIGH:
#             time.sleep(0.09)
#         self.fsm.exp.live_w.toggle_indicator("IR", "on")
#         time.sleep(0.1)
#         self.fsm.exp.live_w.toggle_indicator("IR", "off")
#         print("The mouse entered!")
#         if self.fsm.exp.exp_params["start_trial_time"] is not None:
#             time.sleep(int(self.fsm.exp.exp_params["start_trial_time"]))
#             print("sleep before start trial")
#         self.on_event('IR_stim')
# 
#     def on_event(self, event):
#         if event == 'IR_stim':
#             print("Transitioning from in_port to trial")
#             self.fsm.state = TrialState(self.fsm)

class InPortState(State):
    def __init__(self, fsm):
        super().__init__("port", fsm)
        threading.Thread(target=self.wait_for_event, daemon=True).start()

    def wait_for_event(self):
        timeout_seconds = 15  # timeout
        start_time = time.time()

        while GPIO.input(IR_pin) != GPIO.HIGH:
            if time.time() - start_time > timeout_seconds:
                print("Timeout in InPortState: returning to IdleState")
                self.on_event("timeout")
                return
            time.sleep(0.09)

        self.fsm.exp.live_w.toggle_indicator("IR", "on")
        time.sleep(0.1)
        self.fsm.exp.live_w.toggle_indicator("IR", "off")
        print("The mouse entered!")

        if self.fsm.exp.exp_params["start_trial_time"] is not None:
            time.sleep(int(self.fsm.exp.exp_params["start_trial_time"]))
            print("Sleep before start trial")

        self.on_event('IR_stim')

    def on_event(self, event):
        if event == 'IR_stim':
            print("Transitioning from InPort to Trial")
            self.fsm.state = TrialState(self.fsm)
        elif event == 'timeout':
            print("Transitioning from InPort to Idle due to timeout")
            self.fsm.state = IdleState(self.fsm)

class TrialState(State):
    def __init__(self, fsm):
        super().__init__("trial", fsm)
        self.got_response = None
        self.stop_threads = False
        self.trial_thread = threading.Thread(target=self.run_trial)
        self.trial_thread.start()

    def run_trial(self):
        self.fsm.current_trial.start_time = datetime.now().strftime('%H:%M:%S')  # Get current time
        self.fsm.current_trial.calculate_stim()
        self.fsm.exp.live_w.update_trial_value(self.fsm.current_trial.current_value)

        stim_thread = threading.Thread(target=self.tdt_as_stim)
        input_thread = threading.Thread(target=self.receive_input, args=(lambda: self.stop_threads,))
        
        stim_thread.start()
        input_thread.start()
        stim_thread.join()
        
        self.stop_threads = True
        input_thread.join()

        self.fsm.current_trial.score = self.evaluate_response()
        print("score: " + self.fsm.current_trial.score)
        self.fsm.exp.live_w.update_score(self.fsm.current_trial.score)

        if self.fsm.current_trial.score == 'hit':
            self.give_reward()
        elif self.fsm.current_trial.score == 'fa':
            self.give_punishment()

        self.on_event('trial_over')

    def give_reward(self):
        GPIO.output(valve_pin, GPIO.HIGH)
        #time.sleep(0.03)
        time.sleep(float(self.fsm.exp.exp_params["open_valve_duration"]))
        GPIO.output(valve_pin, GPIO.LOW)

    def give_punishment(self):
        try:
            noise = np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npy')  
            sd.play(noise, len(noise))
            sd.wait()
        finally:
            self.fsm.exp.live_w.toggle_indicator("stim", "off")
            time.sleep(2)

    def tdt_as_stim(self):
        stim_path = self.fsm.current_trial.current_stim_path
        print(stim_path)
        try:
            tone_shape = np.load(stim_path)
            sd.play(tone_shape, len(tone_shape))
            sd.wait()
        finally:
            self.fsm.exp.live_w.toggle_indicator("stim", "off")
            time.sleep(int(self.fsm.exp.exp_params["time_to_lick_after_stim"]))
            print('stimulus done')

    def receive_input(self, stop):
        if self.fsm.exp.exp_params["lick_time_bin_size"] is not None:
            time.sleep(int(self.fsm.exp.exp_params["lick_time_bin_size"]))
        elif self.fsm.exp.exp_params["lick_time"] == "1":
            pass
        elif self.fsm.exp.exp_params["lick_time"] == "2":
            time.sleep(int(self.fsm.exp.exp_params["stimulus_length"]))

        counter = 0
        self.got_response = False
        print('waiting for licks...')
        while not stop():
            if GPIO.input(lick_pin) == GPIO.HIGH:
                self.fsm.exp.live_w.toggle_indicator("lick", "on")
                self.fsm.current_trial.add_lick_time()
                counter += 1
                time.sleep(0.08)
                self.fsm.exp.live_w.toggle_indicator("lick", "off")
                print("lick detected")
            time.sleep(0.08)
        if counter >= int(self.fsm.exp.exp_params["lick_threshold"]):
            self.got_response = True
            print('threshold reached')
        else:
            print('no response')
        print('num of licks:', counter)

    def on_event(self, event):
        if event == 'trial_over':
            time.sleep(0.5)
            self.fsm.current_trial.write_trial_to_csv(self.fsm.exp.txt_file_path)
            if self.fsm.exp.exp_params['ITI_time'] is None:
                while GPIO.input(IR_pin) == GPIO.HIGH:
                    time.sleep(0.09)
                time.sleep(1) # wait one sec after exit- before pass to the next trial
            else:
                time.sleep(int(self.fsm.exp.exp_params['ITI_time']))
            print("Transitioning from trial to idle")
            self.fsm.state = IdleState(self.fsm)

    def evaluate_response(self):
        value = self.fsm.current_trial.current_value
        if value == 'go':
            return 'hit' if self.got_response else 'miss'
        elif value == 'no-go':
            return 'fa' if self.got_response else 'cr'
        elif value == 'catch':
            return 'catch - response' if self.got_response else 'catch - no response'
        
class FiniteStateMachine:

    def __init__(self, experiment=None):
        self.exp = experiment
        self.current_trial = Trial(self)
        self.state = IdleState(self)

    def on_event(self, event):
        self.state.on_event(event)

    def get_state(self):
        return self.state.name


if __name__ == "__main__":
    fsm = FiniteStateMachine()
# class TrialState(State):
#     def __init__(self, fsm):
#         super().__init__("trial", fsm)
#         self.got_response = None
#         self.fsm.current_trial.start_time = datetime.now().strftime('%H:%M:%S')  # Get current time
#         self.fsm.current_trial.calculate_stim()
#         self.fsm.exp.live_w.update_trial_value(self.fsm.current_trial.current_value)
#         self.stop_threads = False
#         self.stim_thread = threading.Thread(target=self.tdt_as_stim)
#         self.input_thread = threading.Thread(target=self.receive_input, args=(lambda: self.stop_threads,))
#         self.stim_thread.start()
#         self.input_thread.start()
#         self.stim_thread.join()
#         self.stop_threads = True
#         self.input_thread.join()
#         self.fsm.current_trial.score = self.evaluate_response()
#         print("score: " + self.fsm.current_trial.score)
#         self.fsm.exp.live_w.update_score(self.fsm.current_trial.score)
#         if self.fsm.current_trial.score == 'hit':
#             self.give_reward()
#         elif self.fsm.current_trial.score == 'fa':
#             self.give_punishment()
#         self.on_event('trial_over')
# 
#     def give_reward(self):
#         GPIO.output(valve_pin, GPIO.HIGH)
#         time.sleep(0.1)
#         GPIO.output(valve_pin, GPIO.LOW)
# 
#     def give_punishment(self):
#         try:
#             noise = np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npy')
#             sd.play(noise, len(noise))
#             sd.wait()
# 
#         finally:
#             self.fsm.exp.live_w.toggle_indicator("stim", "off")
#             time.sleep(2)  # time with no stimulus - that the mouse still can lick
#             print('output stopping')
# 
#     def valve_as_stim(self):
#         GPIO.output(valve_pin, GPIO.HIGH)
#         time.sleep(0.01)
#         GPIO.output(valve_pin, GPIO.LOW)
#         # time.sleep(5)
# 
#     def tdt_as_stim(self):
#         stim_path = self.fsm.current_trial.current_stim_path
#         print(stim_path)
#         try:
#             tone_shape = np.load(stim_path)
#             sd.play(tone_shape, len(tone_shape))
#             sd.wait()
# 
#         finally:
#             self.fsm.exp.live_w.toggle_indicator("stim", "off")
#             time.sleep(int(self.fsm.exp.exp_params["time_to_lick_after_stim"]))  # time for licking after stim
#             print('output stopping')
# 
#     def receive_input(self, stop):
#         if self.fsm.exp.exp_params["lick_time_bin_size"] is not None:  # if the user choose "by time"
#             time.sleep(int(self.fsm.exp.exp_params["lick_time_bin_size"]))
#         elif self.fsm.exp.exp_params["lick_time"] == "1":  # "with stim"
#             pass
#         elif self.fsm.exp.exp_params["lick_time"] == "2":  # "after stim"
#             time.sleep(int(self.fsm.exp.exp_params["stimulus_length"]))
# 
#         counter = 0
#         print('waiting for licks..')
#         self.got_response = False
#         while not stop():
#             if GPIO.input(lick_pin) == GPIO.HIGH:
#                 self.fsm.exp.live_w.toggle_indicator("lick", "on")
#                 self.fsm.current_trial.add_lick_time()
#                 counter += 1
#                 time.sleep(0.08)  # maybe this is problematic if mouse licking is very fast
#                 self.fsm.exp.live_w.toggle_indicator("lick", "off")
#                 print(f"Received input: lick!")
#             time.sleep(0.08)
#         if counter >= int(self.fsm.exp.exp_params["lick_threshold"]):
#             self.got_response = True
#             print('threshold has been reached!')
#         else:
#             print('no response received')
#         print('input thread stopping')
#         print('num of licks: ' + str(counter))
# 
#     def on_event(self, event):
#         if event == 'trial_over':
#             time.sleep(0.5)  # wait for showing the score on the live window before it passes to next trial
#             self.fsm.current_trial.write_trial_to_csv(self.fsm.exp.txt_file_path)
#             if self.fsm.exp.exp_params['ITI_time'] is None:
#                 while GPIO.input(IR_pin) == GPIO.HIGH:  # Waiting for IR rays to not break
#                     time.sleep(0.09)
#             else:
#                 time.sleep(int(self.fsm.exp.exp_params['ITI_time']))
#             print("Transitioning from trial to idle")
#             self.fsm.state = IdleState(self.fsm)
# 
#     def evaluate_response(self):
#         value = self.fsm.current_trial.current_value
#         if value == 'go':
#             if self.got_response:
#                 return 'hit'
#             else:
#                 return 'miss'
#         if value == 'no-go':
#             if self.got_response:
#                 return 'fa'
#             else:
#                 return 'cr'
#         if value == 'catch':
#             if self.got_response:
#                 return 'catch - response'
#             else:
#                 return 'catch - no response'




