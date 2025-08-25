import json
from typing import List, Dict, Any
import trial
from level import Level
from mouse import Mouse
from finite_state_machine import FiniteStateMachine
import tkinter as tk
from tkinter import simpledialog
import threading
import GUI_sections
import live_window
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import state_io
import memory_monitor
import time

###  use those commands on terminal to push changes to git

# cd /home/educage/git_educage2/educage2/pythonProject1
# git add .
# git commit -m ""
# git push
# 
# corrupted size vs. prev_size while consolidating
# 
# Expression 'paTimedOut' failed in 'src/os/unix/pa_unix_util.c', line: 387
# Expression 'PaUnixThread_New( &stream->thread, &CallbackThreadFunc, stream, 1., stream->rtSched )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2998
# Exception in thread Thread-24763:
# Traceback (most recent call last):
#   File "/usr/lib/python3.9/threading.py", line 954, in _bootstrap_inner
#     self.run()
#   File "/usr/lib/python3.9/threading.py", line 892, in run
#     self._target(*self._args, **self._kwargs)
#   File "/home/educage/git_educage2/educage2/pythonProject1/finite_state_machine.py", line 315, in tdt_as_stim
#     sd.play(stim_array, samplerate=sample_rate, blocking=True)
#   File "/home/educage/.local/lib/python3.9/site-packages/sounddevice.py", line 178, in play
#     ctx.start_stream(OutputStream, samplerate, ctx.output_channels,
# Expression 'paTimedOut' failed in 'src/os/unix/pa_unix_util.c', line: 387
# ALSA lib pcm.c:8545:(snd_pcm_recover) underrun occurred
#   File "/home/educage/.local/lib/python3.9/site-packages/sounddevice.py", line 2632, in start_stream
#     self.stream.start()
#   File "/home/educage/.local/lib/python3.9/site-packages/sounddevice.py", line 1124, in start
#     _check(err, 'Error starting stream')
#   File "/home/educage/.local/lib/python3.9/site-packages/sounddevice.py", line 2796, in _check
#     raise PortAudioError(errormsg, err)Expression 'PaUnixThread_New( &stream->thread, &CallbackThreadFunc, stream, 1., stream->rtSched )' failed in 'src/hostapi/alsa/pa_linux_alsa.c', line: 2998
# 

# 
# Process ended with exit code -9.
###
class Experiment:
    def __init__(self, exp_name, mice_dict: dict[str, Mouse] = None, levels_df = None, exp_params = None, auto_start = False):
        """
        יצירת ניסוי חדש
        auto_start: אם True, הניסוי יתחיל אוטומטית אם יש פרמטרים
        """
        print(f"[DEBUG] Experiment.__init__: exp_name={exp_name}, auto_start={auto_start}")
        print(f"[DEBUG] Parameters: exp_params={exp_params is not None}, mice_dict={mice_dict is not None}, levels_df={levels_df is not None}")
        
        self.exp_params = exp_params
        self.fsm = None
        self.live_w = None
        self.levels_df = levels_df
        self.mice_dict = mice_dict
        self.results = []
        self.stim_length = 2
        self.txt_file_name = exp_name
        self.txt_file_path = None
        self.auto_start = auto_start
        
        print(f"[DEBUG] self.auto_start set to: {self.auto_start}")
        
        # יצירת תיקיית הניסוי
        self.new_txt_file(self.txt_file_name)
        
        # יצירת GUI
        self.root = tk.Tk()
        self.GUI = GUI_sections.TkinterApp(self.root, self, exp_name = self.txt_file_name)
        
        # אם יש פרמטרים שנטענו, עדכן את ה-GUI
        if self.auto_start and self.exp_params and self.levels_df is not None and self.mice_dict:
            print("[DEBUG] Updating GUI with loaded data...")
            self.GUI.update_gui_with_loaded_data(self.levels_df, self.mice_dict, self.exp_params)
        
        # הפעלת מערכת ניטור הזיכרון
        self.memory_monitor = memory_monitor.MemoryMonitor(self, threshold_mb=145)
        self.memory_monitor.start_monitoring()
        
        # הפעלת הניסוי
        self.run_experiment()
        self.root.mainloop()
        self.root.destroy()

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
        # Build the path: ./experiments/filename/
        folder_path = os.path.join(os.getcwd(), "experiments", filename)
        os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists

        self.txt_file_path = os.path.join(folder_path,filename+".txt")  

        with open(self.txt_file_path, 'w') as file:
            pass

    def save_minimal_state(self):
        """
        שומר את המצב המינימלי של הניסוי
        """
        if self.exp_params and self.levels_df is not None and self.mice_dict:
            state_io.save_minimal_state(
                self.txt_file_name,
                self.exp_params,
                self.levels_df,
                self.mice_dict,
                self.txt_file_name,
                self.txt_file_path
            )
        else:
            print("Cannot save state - missing required data")

    def get_memory_status(self):
        """מחזיר את סטטוס הזיכרון הנוכחי"""
        if hasattr(self, 'memory_monitor'):
            return self.memory_monitor._get_current_memory_mb()
        return 0
    
    def stop_memory_monitoring(self):
        """עוצר את ניטור הזיכרון"""
        if hasattr(self, 'memory_monitor'):
            self.memory_monitor.stop_monitoring()
    
    def restart_memory_monitoring(self):
        """מתחיל מחדש את ניטור הזיכרון"""
        if hasattr(self, 'memory_monitor'):
            self.memory_monitor.start_monitoring()

    def run_experiment(self):
        # בדיקה אם יש פרמטרים או אם זה אתחול אוטומטי
        print(f"[DEBUG] run_experiment: exp_params={self.exp_params is not None}, auto_start={self.auto_start}")
        
        if self.exp_params is None and not self.auto_start:
            print("[DEBUG] Waiting for parameters...")
            self.root.after(100, lambda: self.run_experiment())  # בדיקה נוספת אחרי 100ms
        else:
            print("Parameters received or auto-start enabled.")
            # המשך עם הניסוי ברגע שהפרמטרים נקבעו
            # התחלת הניסוי בthread נפרד כדי לשמור על הGUI מגיב
            print("[DEBUG] Starting experiment thread...")
            threading.Thread(target=self.start_experiment, daemon=True).start()

    def start_experiment(self):
        # This method runs the actual experiment (on a separate thread)
        print("[DEBUG] start_experiment called")
        
        try:
            # אם זה אתחול אוטומטי, פתח את live window
            if self.auto_start:
                print("Auto-start enabled - opening live window...")
                # המתנה קצרה שהכל יתייצב
                time.sleep(1)
                # יצירת live window באופן סינכרוני
                self.open_live_window()
                print("[DEBUG] Live window opened successfully")
            else:
                print("[DEBUG] Auto-start not enabled")
                
            # יצירת FSM רק אחרי שה-live_w נוצר
            if self.auto_start and (self.live_w is None):
                print("[DEBUG] WARNING: LiveWindow not available, waiting...")
                # המתנה נוספת וניסיון נוסף
                time.sleep(1)
                self.open_live_window()
                
            if self.auto_start and (self.live_w is None):
                print("[DEBUG] ERROR: Failed to create LiveWindow, cannot continue")
                return
                
            fsm = FiniteStateMachine(self)
            self.fsm = fsm
            print("FSM created:", self.fsm)
            

                
        except Exception as e:
            print(f"[DEBUG] Error in start_experiment: {e}")
            import traceback
            traceback.print_exc()

    def run_live_window(self):
        print("[DEBUG] run_live_window called")
        self.root.after(0, self.open_live_window)
        
    def open_live_window(self):
        print("[DEBUG] open_live_window called")
        if self.live_w is None:
            print("[DEBUG] Creating new LiveWindow...")
            try:
                self.live_w = live_window.LiveWindow()
                print("[DEBUG] LiveWindow created successfully")
                # המתנה קצרה לוודא שה-window נוצר בהצלחה
                time.sleep(0.5)
            except Exception as e:
                print(f"[DEBUG] Error creating LiveWindow: {e}")
                self.live_w = None
        else:
            print("[DEBUG] LiveWindow already exists")
        
        # בדיקה שה-live_w אכן נוצר
        if self.live_w is None:
            print("[DEBUG] WARNING: LiveWindow creation failed!")
        else:
            print("[DEBUG] LiveWindow is ready")

    def change_mouse_level(self, mouse: Mouse, new_level: Level):
        mouse.update_level(new_level)

    def save_results(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)

if __name__ == "__main__":
    import sys
    
    # בדיקה אם זה אתחול מחדש
    restart_mode = False
    restart_exp_name = None
    
    # בדיקת ארגומנטים של command line
    if len(sys.argv) > 1 and sys.argv[1] == "--restart":
        if len(sys.argv) > 2:
            restart_exp_name = sys.argv[2]
            restart_mode = True
        else:
            print("Usage: python experiment.py --restart <experiment_name>")
            sys.exit(1)
    
    # אם זה אתחול מחדש, נסה לטעון את המצב
    if restart_mode and restart_exp_name:
        print(f"Attempting to restart experiment: {restart_exp_name}")
        
        # טעינת המצב
        state_data = state_io.load_minimal_state(restart_exp_name)
        
        if state_data:
            print("State loaded successfully, starting experiment...")
            # יצירת הניסוי עם הפרמטרים שנטענו
            experiment = Experiment(
                exp_name=restart_exp_name,
                mice_dict=state_data['mice_dict'],
                levels_df=state_data['levels_df'],
                exp_params=state_data['exp_params'],
                auto_start=True
            )
        else:
            print(f"Failed to load state for {restart_exp_name}")
            sys.exit(1)
    else:
        # הפעלה רגילה - יצירת תיקיית ניסוי חדשה
        created_folder_name = None

        def create_experiment_folder():
            global created_folder_name

            exp_name = entry.get().strip()
            if not exp_name:
                messagebox.showwarning("Input Error", "Please enter a valid experiment name.")
                return

            date_str = datetime.now().strftime("%d_%m_%Y")
            base_dir = "experiments"
            os.makedirs(base_dir, exist_ok=True)

            folder_name = f"{exp_name}_{date_str}"
            full_path = os.path.join(base_dir, folder_name)

            if os.path.exists(full_path):
                # בדיקה אם יש קובץ מצב זמין
                if state_io.check_if_restart_available(folder_name):
                    answer = messagebox.askyesno("Restart Available", 
                        f"The folder '{folder_name}' exists and has a saved state.\nDo you want to restart the experiment?")
                    if answer:
                        # אתחול מחדש
                        created_folder_name = folder_name
                        root.destroy()
                        return
                
                # שאלה אם רוצים להשתמש בתיקייה קיימת
                answer = messagebox.askyesno("Folder Exists", f"The folder '{folder_name}' already exists.\nDo you want to use it?")
                if not answer:
                    return  # לא לעשות כלום, לתת למשתמש לשנות את השם או לבטל
            else:
                os.makedirs(full_path)

            created_folder_name = folder_name
            root.destroy()

        # יצירת חלון הGUI
        root = tk.Tk()
        root.title("Experiment Setup")
        root.geometry("300x120")

        tk.Label(root, text="Enter Experiment Name:").pack(pady=10)

        entry = tk.Entry(root, width=30)
        entry.insert(0, "exp")  # טקסט ברירת מחדל
        entry.pack()

        tk.Button(root, text="Create Folder", command=create_experiment_folder).pack(pady=10)

        root.mainloop()

        # יצירת הניסוי
        if created_folder_name:
            experiment = Experiment(exp_name=created_folder_name)

