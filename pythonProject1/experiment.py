import json
from typing import List, Dict, Any
from reward_and_punishment_system import RewardAndPunishmentSystem
import trial
from level import Level
import data_analysis
from exp_parameters import ExpParameters
from mouse import Mouse
from finite_state_machine import FiniteStateMachine
from stimulus import Stimulus


class Experiment:
    def __init__(self,exp_name, mice_dict: dict[str, Mouse], levels_dict: dict[int:Level]):
        self.prams = ExpParameters()
        self.levels_dict = levels_dict
        self.mice_dict = mice_dict#self.create_mice(mice_dict)
        self.results = []
        self.txt_file_name = exp_name
        self.new_txt_file(self.txt_file_name)
        self.fsm = self.run_experiment()


    def new_txt_file(self, filename):
        with open(self.txt_file_name, 'w') as file:
            file.write("Experiment Log\n")
            file.write("=" * 30 + "\n")

    def log_parameters(self, **trial_params):
        # This writes the given parameters to the text file
        with open(self.txt_file_name, 'a') as file:
            for key, value in trial_params.items():
                file.write(f"{key}: {value}\n")
            file.write("-" * 30 + "\n")

    def create_mice(self, mice_dict):
        mice = dict()
        for id in mice_dict:
            level = self.levels_dict[mice_dict[id]]
            mice[id] = Mouse(id, level)
        return mice

    def run_experiment(self):
        # the main loop?
        fsm = FiniteStateMachine(self.prams,self.levels_dict, self.mice_dict)
        return fsm

    def pause_experiment(self):
        pass

    def resume_experiment(self):
        pass

    def finish_experiment(self):
        pass
    def run_trial(self, mouse: Mouse):
        parameters = mouse.level.get_parameters()

        # Example stimulus interaction (simply mocked for demonstration)
        stimulus = Stimulus(stimulus_id=1, stimulus_type='light', duration=2.0)
        stimulus.play()

        # Simulated response (In a real scenario, this would come from the user's input)
        response = 'correct'  # Replace this with actual response capturing.

        reward_system = RewardAndPunishmentSystem()
        reward_type = reward_system.evaluate_response(response)

        # Record the result
        trial_data = {
            'mouse_id': mouse.id,
            'level': mouse.level.level_id,
            'response': response,
            'outcome': reward_type
        }
        mouse.record_performance(trial_data)
        self.results.append(trial_data)

        # Deliver reward or punishment
        if reward_type == 'reward':
            reward_system.deliver_reward()
        else:
            reward_system.impose_punishment()

    def change_mouse_level(self, mouse: Mouse, new_level: Level):
        mouse.update_level(new_level)

    def save_results(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)

#
#
#
#


# Example usage:
if __name__ == "__main__":

    # Create levels
    level_1 = Level(level_id=1, parameters={'stimuli': ['noise1', 'sound'], 'reaction_time': '2s'})
    level_2 = Level(level_id=2, parameters={'stimuli': ['noise2', 'visual'], 'reaction_time': '1s'})

    # Create mice
    mouse_1 = Mouse(mouse_id='0007B80FBC', level=level_1)
    mouse_2 = Mouse(mouse_id='0007DECB4A', level=level_2)
    mouse_3 = Mouse(mouse_id='0007DEC04C', level=level_2)

    # Create an experiment
    experiment = Experiment(exp_name = 'exp1', mice_dict={mouse_1.get_id():mouse_1, mouse_2.get_id():mouse_2}, levels_dict={1: level_1, 2: level_2})
    # Run trials
    # experiment.run_trial(mouse_1)
    # experiment.run_trial(mouse_2)
    #
    # # Save results to a file
    # experiment.save_results('experiment_results.json')

    print("Experiment completed and results saved.")
    print("control it from goggle remote!")
    print("rasp_commit!")
