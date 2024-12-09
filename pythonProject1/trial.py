from datetime import datetime
import csv
import random
class Trial:
    def __init__(self,fsm):
        self.fsm = fsm
        self.current_mouse = None
        self.current_exp_parameters = None
        self.performance_data = None
        self.score = None
        self.start_time = None 

    def update_current_mouse(self, new_mouse: 'Mouse'):
        self.current_mouse = new_mouse
    # def record_performance(self,txt_file_name):
    #     pass
    # #     def log_parameters(self, **trial_params):
    #     # This writes the given parameters to the text file
    #     with open(self.txt_file_name, 'a') as file:
    #         for key, value in trial_params.items():
    #             file.write(f"{key}: {value}\n")
    #         file.write("-" * 30 + "\n")

    def save_trial(self):
        pass

    def update_score(self, score): # hit\miss\fa\cr
        self.score = score

    def calculate_stim(self): #determine if the trial is go\nogo\catch using random
        level_name = self.current_mouse.get_level()
        level_rows = self.fsm.levels_df.loc[self.fsm.levels_df['Level Name'] == level_name]
        probabilities = level_rows["Probability"].tolist()
        indices = level_rows["Index"].tolist()
        total_probability = sum(probabilities)
        normalized_probabilities = [p / total_probability for p in probabilities]
        chosen_index = random.choices(indices, weights=normalized_probabilities, k=1)[0]
        return self.fsm.levels_df.loc[(self.fsm.levels_df['Level Name'] == level_name)&(self.fsm.levels_df['Index'] == chosen_index)]

    def end_trial(self): # the trial is over - go to save it
        pass
    
    def clear_trial(self):
        self.current_mouse = None
        self.current_exp_parameters = None
        self.performance_data = None
        self.score = None
        
# Function to write trial results
    def write_trial_to_csv(self, txt_file_name):
        header = ['date', 'start time', 'end time','trial number', 'mouse ID', 'level', 'go\no-go','stim', 'score'] # Define the header if the file does not exist yet
        current_datetime = datetime.now()
        date = current_datetime.strftime('%Y-%m-%d')  # Get current date
        end_time = current_datetime.strftime('%H:%M:%S')  # Get current time
        trial_data = [date, self.start_time, end_time, self.current_mouse.id, self.current_mouse.level, 'go\no-go','stim', 'score' ]
        with open(txt_file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Check if the file is empty to write the header
            if file.tell() == 0:  # Check if the file is empty
                writer.writerow(header)  # Write the header
            writer.writerow(trial_data)

# Example trial results
# for trial_num in range(1, 6):  # Simulating 5 trials
#     trial_result = [trial_num, 1000, 5, 2, 0.1, 44100]  # Example data for one trial
#     write_trial_to_csv(trial_result)
#     print(f"Trial {trial_num} results written to 'experiment_trials.csv'")
#     
    
"""זה לק שנמצא כרגע במחלקת מערכת עונש ותגמול"""
    # def evaluate_response(self, response):
    #     if response.lower() == 'correct':
    #         return 'reward'
    #     else:
    #         return 'punishment'
    #
    # def deliver_reward(self):
    #     print("Delivering reward.")
    #
    # def impose_punishment(self):
    #     print("Imposing punishment.")

