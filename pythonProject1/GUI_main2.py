import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import scrolledtext
import serial
import threading
import General_fanctions
# Main application
class MainApp:
    def __init__(self, master):
        self.master = master
        master.title("Main Window")
        General_fanctions.center_the_window(master,'500x300')
        
        # Initial parameter
        self.mice_list = None
        # Create a LabelFrame to act as a container for the table
        self.frame = tk.LabelFrame(master, text="Mice List", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)
        General_fanctions.create_table(self.mice_list,self.frame)

        # Button to open the new parameter window
        self.get_parameter_button = tk.Button(master, text="Update mice table", command=self.open_parameter_window)
        self.get_parameter_button.pack(pady=10)

    def set_new_mice_list(self,data_list):
        self.mice_list = data_list
        General_fanctions.create_table(self.mice_list,self.frame)
        
    def open_parameter_window(self):
                
        def read_from_serial():
    
            try:
                # Setup Serial Connection (adjust COM4 and 9600 to your needs)
                ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=0.01)#timeout=1  # Change '/dev/ttyS0' to the detected port
                while True:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()
                        display_data(line)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
            finally:
                try:
                    ser.close()
                except Exception:
                    pass
        def display_data(data):
            # Allow editing the text widget by setting it to normal
            self.data_display.config(state=tk.NORMAL)
            
            # Clear the existing text
            self.data_display.delete("1.0", tk.END)
            
            # Insert the new data
            self.data_display.insert(tk.END, data + "\n")
            
            # Automatically scroll to the end (useful if it would add multiple lines)
            self.data_display.yview(tk.END)
            
            # Disable editing again
            self.data_display.config(state=tk.DISABLED)
            
        def add_to_list():
            # Extract the last line from data_display
            data_display_content = self.data_display.get("1.0", tk.END).strip().split("\n")
            if data_display_content:
                last_line = data_display_content[-1]
                if last_line not in self.unique_data_display.get("1.0", tk.END):
                    self.unique_data_display.config(state=tk.NORMAL)
                    self.unique_data_display.insert(tk.END, last_line + "\n")
                    self.unique_data_display.config(state=tk.DISABLED)
                    
        def clear_box():
            # Clear the existing text
            self.unique_data_display.config(state=tk.NORMAL)
            self.unique_data_display.delete("1.0", tk.END)
            self.unique_data_display.config(state=tk.DISABLED)

        def save_and_close():
            text_content = self.unique_data_display.get("1.0", tk.END).strip()
            
            # Split the content by lines
            data_list = text_content.split("\n")
            print(data_list)
            # Return the list
            print(self.mice_list)
            #self.mice_list = data_list
            self.set_new_mice_list(data_list)
            print(self.mice_list)
            print(f"Mice list received and saved: {self.mice_list}")  
            self.parameter_window.destroy()
 
        # Create a new Toplevel window
        self.parameter_window = tk.Toplevel(self.master)
        self.parameter_window.title("mice table")
        
        General_fanctions.center_the_window(self.parameter_window,'500x300')

        
        # Data Display Box for serial readings
        self.data_display = scrolledtext.ScrolledText(self.parameter_window, height=15, width=15, state=tk.DISABLED)
        self.data_display.pack(side=tk.LEFT, padx=5, pady=5)

        # Unique Data Display Box
        self.unique_data_display = scrolledtext.ScrolledText(self.parameter_window, height=15, width=15, state=tk.DISABLED)
        self.unique_data_display.pack(side=tk.RIGHT, padx=5, pady=5)

        # Add to List Button
        self.add_to_list_button = tk.Button(self.parameter_window, text="Add to List", command=add_to_list)
        self.add_to_list_button.pack()


        # Clear Button
        self.clear_button = tk.Button(self.parameter_window, text="Clear", command=clear_box)
        self.clear_button.pack()

        # Done Button
        self.done_button = tk.Button(self.parameter_window, text="Done", command=save_and_close)
        self.done_button.pack()

        threading.Thread(target=read_from_serial, daemon=True).start()
        # Wait for the parameter_window to close before proceeding
        self.parameter_window.wait_window()  # This makes the window modal-like
              

# Initialize the main window
root = tk.Tk()
app = MainApp(root)
root.mainloop()


