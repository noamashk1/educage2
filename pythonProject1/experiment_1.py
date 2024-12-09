import json
from typing import List, Dict, Any
from reward_and_punishment_system import RewardAndPunishmentSystem
import trial
from level_1 import Level
import data_analysis
#from exp_parameters import ExpParameters
from mouse_1 import Mouse
from finite_state_machine import FiniteStateMachine
from stimulus import Stimulus
import tkinter as tk
import threading
import GUI_sctions

class Experiment:
    def __init__(self,exp_name, mice_dict: dict[str, Mouse] = None, levels_df = None):
        self.exp_params = None#ExpParameters(self)
        self.fsm = None
        self.levels_df = levels_df
        self.mice_dict = mice_dict#self.create_mice(mice_dict)
        self.results = []
        self.txt_file_name = exp_name
        self.new_txt_file(self.txt_file_name)
        #self.root = root
        self.root = tk.Tk()
        #self.GUI = App(self.root,self)
        self.GUI = GUI_sctions.TkinterApp(self.root, self, exp_name = self.txt_file_name)
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

    # def create_mice(self, mice_dict):
    #     mice = dict()
    #     for id in mice_dict:
    #         level = self.levels_dict[mice_dict[id]]
    #         mice[id] = Mouse(id, level)
    #     return mice

#     def run_experiment(self):
#          # Check periodically if parameters have been set
#         if self.exp_params is None:
#             print("Waiting for parameters...")
#             self.root.after(100, lambda: self.run_experiment())  # Check every 100ms
#         else:
#             fsm = FiniteStateMachine(self.exp_params, self.mice_dict,self.levels_dict)
#             self.fsm=fsm
            
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
        fsm = FiniteStateMachine(self.exp_params, self.mice_dict, self.levels_df, self.txt_file_name)
        self.fsm = fsm
        print("FSM created:", self.fsm)

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
