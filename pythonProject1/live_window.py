import tkinter as tk


class LiveWindow:
    def __init__(self):
        # Create the main window
        self.root = tk.Toplevel()
        self.root.title("Live Window")
        self.root.geometry("300x530")  # Set the window dimensions to 400x600 pixels
#         self.root = tk.Tk()
#         self.root.title("Live Window")
#         self.root.geometry("300x480")  # Set the window dimensions to 400x600 pixels

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
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)  # Center the button frame vertically with padding

        # Create buttons
        pause_button = tk.Button(button_frame, text="Pause", command=self.pause_experiment)
        pause_button.pack(side='left', padx=5)

        continue_button = tk.Button(button_frame, text="Continue", command=self.continue_experiment)
        continue_button.pack(side='left', padx=5)

        end_button = tk.Button(button_frame, text="End Experiment", command=self.end_experiment)
        end_button.pack(side='left', padx=5)

        # Start the GUI event loop
        #self.root.mainloop()

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


#     def toggle_indicator(self, canvas):
#         # Check current state and toggle the indicator light
#         current_color = canvas.itemcget(self.indicator_circle, "fill")  # Get current fill color
#         new_color = "gray" if current_color == "green" else "green"  # Toggle the state
#         canvas.itemconfig(self.indicator_circle, fill=new_color)  # Change circle color
        
    def toggle_indicator(self, bulb_name, turn_to):
        # Check current state and toggle the indicator light
        if turn_to == "on":
            fill = "green"
        elif turn_to == "off":
            fill = "gray"
        if bulb_name =="Idle":
            self.idle_bulb.itemconfig(self.indicator_circle, fill=fill)  
        elif bulb_name =="port":
            self.in_port_bulb.itemconfig(self.indicator_circle, fill=fill)
        elif bulb_name =="trial":
            self.trial_bulb.itemconfig(self.indicator_circle, fill=fill)
        elif bulb_name =="IR":
            self.ir_bulb.itemconfig(self.indicator_circle, fill=fill)
        elif bulb_name =="lick":
            self.lick_bulb.itemconfig(self.indicator_circle, fill=fill)
        elif bulb_name =="stim":
            self.stimulus_bulb.itemconfig(self.indicator_circle, fill=fill)

        
    def deactivate_states_indicators(self, state_name):
        self.idle_bulb.itemconfig(self.indicator_circle, fill="gray")  
        self.in_port_bulb.itemconfig(self.indicator_circle, fill="gray") 
        self.trial_bulb.itemconfig(self.indicator_circle, fill="gray")
        if state_name =="Idle":
            self.idle_bulb.itemconfig(self.indicator_circle, fill="green")  
        elif state_name =="port":
            self.in_port_bulb.itemconfig(self.indicator_circle, fill="green") 
        else:
            self.trial_bulb.itemconfig(self.indicator_circle, fill="green")
            

    def pause_experiment(self):
#         self.toggle_indicator(self.lick_light)  # Toggle Lick light
#         self.toggle_indicator(self.ir_light)  # Toggle IR light
#         self.toggle_indicator(self.stimulus_light)  # Toggle Stimulus light
        print("Experiment paused")

    def continue_experiment(self):
#         self.toggle_indicator(self.idle_light)  # Toggle Idle light
#         self.toggle_indicator(self.in_port_light)  # Toggle In Port light
#         self.toggle_indicator(self.trial_light)  # Toggle Trial light

        print("Experiment continued")

    def end_experiment(self):
        print("Experiment ended")
#         self.toggle_indicator(self.trial_light)  # Toggle Trial light
        #self.root.destroy()  # Close the window

    def update_last_rfid(self, rfid):
        self.last_rfid_value.config(text=rfid)  # Update last RFID label

    def update_score(self, score):
        self.score_value.config(text=str(score))  # Update score label
        
    def update_level(self, level):
        self.level_value.config(text=str(level))  # Update score label
        
    def update_trial_value(self, trial_value):
        self.trial_value.config(text=str(trial_value))  # Update score label

# Example usage
#live_window = LiveWindow()

