import main_GUI
import tkinter as tk
# main.py
import subprocess
# file_with_class.py
import threading
import main_GUI



class ExpParameters:
    def __init__(self,exp):

        self.root = tk.Tk()
        self.app = main_GUI.App(self.root,exp)
        self.root.mainloop()
        self.params =None
        # threading.Thread(target=main_GUI.run, daemon=True).start()
        # print("GUI started in background.")

        # self.IR_no_RFID='Take the last detected RFID' # What to do if an IR break was detected but not RFID. Option 1: Don't start a trail. Option 2: Take the last detected RFID
        # self.start_trial='immediately' # How long to start giving stimulation after IR detection
        # self.lick_threshold = 4 #The number of licks considered as a response of the mouse
        # self.time_start_count_licks = 'along with the stimulus' # When to start counting the licks. Options: along with the stimulus, after the stimulus, after a given number of milliseconds
        # self.ITI = 3 # Inter Trial Interval
        pass
    def print_params(self):
        pass

    def set_param(self, mouse_id, col):
        pass

    def get_param(self, mouse_id, col):
        pass

# Example usage
if __name__ == "__main__":
    my_instance = ExpParameters()
    # The GUI will appear automatically when MyClass is instantiated
