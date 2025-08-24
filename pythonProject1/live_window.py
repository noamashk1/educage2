import tkinter as tk
import sys
import threading


class LiveWindow:
    def __init__(self):
        # Create the main window
        print('live_window constructor')
        self.root = tk.Toplevel()
        self.root.title("Live Window")
        self.root.geometry("300x530")  # Set the window dimensions to 400x600 pixels
        
        self.pause = False
        # Create title label
        title_label = tk.Label(self.root, text="Live Window", font=("Arial", 16))
        title_label.pack(pady=(10, 5), anchor='w')  # Left align title with some padding

        # Subtitle for FSM states
        fsm_label = tk.Label(self.root, text="Current state:", font=("Arial", 14))
        fsm_label.pack(anchor='w', padx=(10, 5), pady=(10, 5))  # Left align subtitle with padding

        # Create indicator lights for FSM states
        self.idle_bulb = self.create_indicator("Idle")
        self.in_port_bulb = self.create_indicator("In Port")
        self.trial_bulb = self.create_indicator("Trial")

        # Subtitle for status
        status_label = tk.Label(self.root, text="status:", font=("Arial", 14))
        status_label.pack(anchor='w', padx=(10, 5), pady=(10, 5))  # Left align subtitle with padding

        # Label for last RFID with frame
        self.create_labeled_frame("last RFID:")
        
        # Label for the level of the last RFID 
        self.create_labeled_frame("level:")

        # Create indicator bulbs for additional status
        self.lick_bulb = self.create_indicator("Lick")
        self.ir_bulb = self.create_indicator("IR")
        self.stimulus_bulb = self.create_indicator("Stimulus")

        # Label for score with frame
        self.create_labeled_frame("trial value:")
        
        # Label for score with frame
        self.create_labeled_frame("score:")

        # Frame for buttons to center them
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)  # Center the button frame vertically with padding

        # Create buttons
        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.pause_experiment)
        self.pause_button.pack(side='left', padx=5)

        self.continue_button = tk.Button(self.button_frame, text="Continue", command=self.continue_experiment)
        self.continue_button.pack(side='left', padx=5)
        self.continue_button.config(state=tk.DISABLED)

        self.end_button = tk.Button(self.button_frame, text="End Experiment", command=self.end_experiment)
        self.end_button.pack(side='left', padx=5)


    def create_indicator(self, name):
        frame = tk.Frame(self.root)
        frame.pack(anchor='w', padx=(10, 5), pady=(5, 2))  # Left align indicator frame with padding

        # Create circle for the indicator
        canvas = tk.Canvas(frame, width=20, height=20)
        canvas.pack(side='left')

        # Draw a gray circle
        self.indicator_circle = canvas.create_oval(5, 5, 15, 15, fill="gray", outline="")

        # Label for the indicator
        label = tk.Label(frame, text=name)
        label.pack(side='left', padx=(5, 0))  # Add space between circle and label

        return canvas

    def create_labeled_frame(self, label_text):
        # Frame for the label with a border
        frame = tk.Frame(self.root)
        frame.pack(anchor='w', padx=10, pady=(5, 2))  # Left align and add some padding

        # Create label for the text
        label = tk.Label(frame, text=label_text, font=("Arial", 12))
        label.pack(side='left', padx=(5, 0))  # Left align the label

        # Create label for the value with a background color for visibility
        value_label = tk.Label(frame, text="", font=("Arial", 12), bg="lightgray", width=20)
        value_label.pack(side='left', padx=(5, 5))  # Add space after the value label

        # Store reference to the value label
        if label_text == "last RFID:":
            self.last_rfid_value = value_label  # Store reference to the last RFID label
        elif label_text == "level:":
            self.level_value = value_label  
        elif label_text == "trial value:":
            self.trial_value = value_label  
        elif label_text == "score:":
            self.score_value = value_label  

        
    def toggle_indicator(self, bulb_name, turn_to):
        """מחליף את מצב האינדיקטור בצורה בטוחה עם threads"""
        try:
            if turn_to == "on":
                fill = "green"
            elif turn_to == "off":
                fill = "gray"
            else:
                return
            
            # בחירת האינדיקטור הנכון
            if bulb_name == "Idle":
                bulb = self.idle_bulb
            elif bulb_name == "port":
                bulb = self.in_port_bulb
            elif bulb_name == "trial":
                bulb = self.trial_bulb
            elif bulb_name == "IR":
                bulb = self.ir_bulb
            elif bulb_name == "lick":
                bulb = self.lick_bulb
            elif bulb_name == "stim":
                bulb = self.stimulus_bulb
            else:
                return
            
            # עדכון בטוח
            self._safe_update_indicator(bulb, fill)
            
        except Exception as e:
            print(f"Error toggling indicator {bulb_name}: {e}")
    
    def _safe_update_indicator(self, bulb, fill):
        """עדכון בטוח של אינדיקטור מה-main thread"""
        try:
            if hasattr(self, 'root') and self.root and bulb:
                if threading.current_thread() == threading.main_thread():
                    # זה ה-main thread - עדכון ישיר
                    bulb.itemconfig(self.indicator_circle, fill=fill)
                else:
                    # זה thread אחר - עדכון דרך main thread
                    self.root.after(0, lambda: bulb.itemconfig(self.indicator_circle, fill=fill))
        except Exception as e:
            print(f"Error in safe indicator update: {e}")

        
    def deactivate_states_indicators(self, state_name):
        """מעדכן את מצב האינדיקטורים בצורה בטוחה עם threads"""
        try:
            # כיבוי כל האינדיקטורים
            self._safe_update_indicator(self.idle_bulb, "gray")
            self._safe_update_indicator(self.in_port_bulb, "gray")
            self._safe_update_indicator(self.trial_bulb, "gray")
            
            # הפעלת האינדיקטור הנכון
            if state_name == "Idle":
                self._safe_update_indicator(self.idle_bulb, "green")
            elif state_name == "port":
                self._safe_update_indicator(self.in_port_bulb, "green")
            else:
                self._safe_update_indicator(self.trial_bulb, "green")
                
        except Exception as e:
            print(f"Error updating state indicators: {e}")
            

    def pause_experiment(self):
        self.pause = True
#         self.main_GUI.able_parameters_buttons()
        self.continue_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        print("Experiment paused")

    def continue_experiment(self):
        self.pause = False
#         self.main_GUI.disable_parameters_buttons()
        self.pause_button.config(state=tk.NORMAL)
        self.continue_button.config(state=tk.DISABLED)
        print("Experiment continued")

    def end_experiment(self):
        print("Experiment ended")
        self.root.quit()

    def update_last_rfid(self, rfid):
        """מעדכן את ה-RFID האחרון בצורה בטוחה עם threads"""
        try:
            # בדיקה שהחלון עדיין קיים
            if hasattr(self, 'root') and self.root:
                # בדיקה אם זה ה-main thread
                if threading.current_thread() == threading.main_thread():
                    # זה ה-main thread - עדכון ישיר
                    self.last_rfid_value.config(text=rfid)
                else:
                    # זה thread אחר - עדכון דרך main thread
                    self.root.after(0, lambda: self._safe_update_rfid(rfid))
            else:
                print("Live window root not available for RFID update")
        except Exception as e:
            print(f"Error updating RFID: {e}")
    
    def _safe_update_rfid(self, rfid):
        """עדכון בטוח של RFID מה-main thread"""
        try:
            if hasattr(self, 'last_rfid_value') and self.last_rfid_value:
                self.last_rfid_value.config(text=rfid)
        except Exception as e:
            print(f"Error in safe RFID update: {e}")

    def update_score(self, score):
        """מעדכן את התוצאה בצורה בטוחה עם threads"""
        self._safe_update_widget(self.score_value, str(score))
        
    def update_level(self, level):
        """מעדכן את הרמה בצורה בטוחה עם threads"""
        self._safe_update_widget(self.level_value, str(level))
        
    def update_trial_value(self, trial_value):
        """מעדכן את ערך הניסוי בצורה בטוחה עם threads"""
        self._safe_update_widget(self.trial_value, str(trial_value))
    
    def _safe_update_widget(self, widget, value):
        """עדכון בטוח של widget מה-main thread"""
        try:
            if hasattr(self, 'root') and self.root and widget:
                if threading.current_thread() == threading.main_thread():
                    # זה ה-main thread - עדכון ישיר
                    widget.config(text=value)
                else:
                    # זה thread אחר - עדכון דרך main thread
                    self.root.after(0, lambda: widget.config(text=value))
        except Exception as e:
            print(f"Error in safe widget update: {e}")

# Example usage
#live_window = LiveWindow()

