import json
from typing import List, Dict, Any
from reward_and_punishment_system import RewardAndPunishmentSystem
import trial
from level import Level
import data_analysis
#from exp_parameters import ExpParameters
from mouse import Mouse
from finite_state_machine import FiniteStateMachine
from stimulus import Stimulus
import tkinter as tk
from tkinter import simpledialog
import threading
import GUI_sections
import live_window

###
# cd /home/educage/git_educage2/educage2/pythonProject1
# git add .
# git commit -m ""
# git push
###
class Experiment:
    def __init__(self,exp_name, mice_dict: dict[str, Mouse] = None, levels_df = None):
        
#         root = tk.Tk()
#         root.withdraw()  # Hide the root window
# 
#         # Show dialog box to get the experiment name
#         self.txt_file_name = simpledialog.askstring("Input", "Please enter the experiment name:")
#         root.destroy()
#         
        
        self.exp_params = None#ExpParameters(self)
        self.fsm = None
        self.live_w = None
        self.levels_df = levels_df
        self.mice_dict = mice_dict#self.create_mice(mice_dict)
        self.results = []
        self.txt_file_name = exp_name
        self.new_txt_file(self.txt_file_name)
        self.root = tk.Tk()
        self.GUI = GUI_sections.TkinterApp(self.root, self, exp_name = self.txt_file_name)
        self.run_experiment()
        self.root.mainloop()
        

    def set_parameters(self, parameters):
        """This method is called by App when the OK button is pressed."""
        self.exp_params = parameters
        print("Parameters set in Experiment:", self.exp_params)

    def set_mice_dict(self, mice_dict):
        """This method is called by App when the OK button is pressed."""
        self.mice_dict = mice_dict

    def set_levels_df(self, levels_df):
        """This method is called by App when the OK button is pressed."""
        self.levels_df = levels_df
        
    def new_txt_file(self, filename):
        with open(self.txt_file_name, 'w') as file:
            pass

#     def log_parameters(self, **trial_params):
#         # This writes the given parameters to the text file
#         with open(self.txt_file_name, 'a') as file:
#             for key, value in trial_params.items():
#                 file.write(f"{key}: {value}\n")
#             file.write("-" * 30 + "\n")


    def run_experiment(self):
        # Check periodically if parameters have been set
        if self.exp_params is None:
            #print("Waiting for parameters...")
            self.root.after(100,lambda: self.run_experiment())  # Check again after 100ms
        else:
            print("Parameters received.")
            # Proceed with the experiment once parameters are set
            # Start experiment in a separate thread to keep the GUI responsive
            threading.Thread(target=self.start_experiment).start()

    def start_experiment(self):
        # This method runs the actual experiment (on a separate thread)
        print("Experiment started with parameters:", self.exp_params)
        fsm = FiniteStateMachine(self.exp_params, self.mice_dict, self.levels_df, self.txt_file_name, self.live_w)
        self.fsm = fsm
        print("FSM created:", self.fsm)
        
    def run_live_window(self):
        self.root.after(0, self.open_live_window)
        #self.open_live_window()
        
    def open_live_window(self):
        if self.live_w is None:
            self.live_w = live_window.LiveWindow()

#     def open_live_window(self):
#         if self.live_w is None:
#             try:
#                 print("Attempting to create LiveWindow...")
#                 self.live_w = live_window.LiveWindow()  # Assuming LiveWindow is defined correctly
#                 print("LiveWindow created successfully.")
#                 print(f"self.live_w: {self.live_w}")  # Check that live_w is properly assigned
#             except Exception as e:
#                 print(f"An error occurred while creating LiveWindow: {e}")
# 
#         print("Reached the end of open_live_window function.")
        
    

#     def pause_experiment(self):
#         pass
# 
#     def resume_experiment(self):
#         pass
# 
#     def finish_experiment(self):
#         pass
#     def run_trial(self, mouse: Mouse):
#         parameters = mouse.level.get_parameters()
# 
#         # Example stimulus interaction (simply mocked for demonstration)
#         stimulus = Stimulus(stimulus_id=1, stimulus_type='light', duration=2.0)
#         stimulus.play()
# 
#         # Simulated response (In a real scenario, this would come from the user's input)
#         response = 'correct'  # Replace this with actual response capturing.
# 
#         reward_system = RewardAndPunishmentSystem()
#         reward_type = reward_system.evaluate_response(response)
# 
#         # Record the result
#         trial_data = {
#             'mouse_id': mouse.id,
#             'level': mouse.level.level_id,
#             'response': response,
#             'outcome': reward_type
#         }
#         mouse.record_performance(trial_data)
#         self.results.append(trial_data)
# 
#         # Deliver reward or punishment
#         if reward_type == 'reward':
#             reward_system.deliver_reward()
#         else:
#             reward_system.impose_punishment()

    def change_mouse_level(self, mouse: Mouse, new_level: Level):
        mouse.update_level(new_level)

    def save_results(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)



 # Example usage:
if __name__ == "__main__":
# 
#     # Create levels
#     level_1 = Level(level_id=1, parameters={'stimuli': ['noise1', 'sound'], 'reaction_time': '2s'})
#     level_2 = Level(level_id=2, parameters={'stimuli': ['noise2', 'visual'], 'reaction_time': '1s'})
# 
#     # Create mice
#     mouse_1 = Mouse(mouse_id='0007B80FBC', level= "level_1")
#     mouse_2 = Mouse(mouse_id='0007DECB4A', level="level_2")
#     mouse_3 = Mouse(mouse_id='0007DEC04C', level="level_2")
# 
#     # Create an experiment
     experiment = Experiment(exp_name = 'exp1')#, mice_dict={mouse_1.get_id():mouse_1, mouse_2.get_id():mouse_2}, levels_df={1: level_1, 2: level_2})
#     # Run trials
#     # experiment.run_trial(mouse_1)
#     # experiment.run_trial(mouse_2)
#     #
#     # # Save results to a file
#     # experiment.save_results('experiment_results.json')
# 
#     print("Experiment completed and results saved.")
#     print("control it from goggle remote!")
#     print("rasp_commit!")
