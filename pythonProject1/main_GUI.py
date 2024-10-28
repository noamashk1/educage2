# import tkinter as tk
# from tkinter import filedialog, messagebox
# from tkinter import ttk
# import tkinter.font as tkFont
#
# class App:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Data Analysis App")
#
#         # Set window size
#         window_width = 600
#         window_height = 600
#         screen_width = self.root.winfo_screenwidth()
#         screen_height = self.root.winfo_screenheight()
#
#         # Calculate the position to center the window
#         x_position = (screen_width // 2) - (window_width // 2)
#         y_position = (screen_height // 2) - (window_height // 2)
#
#         # Set the geometry of the window
#         self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
#
#         # Increase font size
#         self.font_style = tkFont.Font(family="Helvetica", size=13)
#
#         # Button to select files
#         self.select_button = tk.Button(root, text="Select Excel Files", command=self.select_excel_file, font=self.font_style)
#         self.select_button.pack(pady=10)
#
#         # Store the selected file path
#         self.selected_file = None
#
#         # Radiobuttons for display options
#         self.display_option = tk.StringVar(value='1')  # Default to "By Sessions"
#         self.radiobuttons_frame = tk.Frame(root)
#         self.radiobuttons_frame.pack(pady=10)
#         self.custom_input_label = tk.Label(self.radiobuttons_frame, text=" When to start counting the licks:", font=self.font_style)
#         self.custom_input_label.pack(anchor=tk.W)
#
#         # Radio buttons without automatic analysis
#         tk.Radiobutton(self.radiobuttons_frame, text="with stim", command=self.time_selected, variable=self.display_option, value='1',
#                        font=self.font_style).pack(anchor=tk.W)
#         tk.Radiobutton(self.radiobuttons_frame, text="after stim", command=self.time_selected, variable=self.display_option, value='2',
#                        font=self.font_style).pack(anchor=tk.W)
#         tk.Radiobutton(self.radiobuttons_frame, text="By time", command=self.time_selected, variable=self.display_option, value='3',
#                        font=self.font_style).pack(anchor=tk.W)#anchor=tk.W
#
#         # Option menu for additional choices
#
#         self.option_var = tk.StringVar(value="Option 1")  # Default value
#         self.option_menu = ttk.OptionMenu(root, self.option_var, "Option 1", "Option 1", "Option 2", "Custom", command=self.option_selected)
#         self.option_menu.pack(pady=10)
#
#         # Custom input section (initially hidden)
#         self.custom_input_frame = tk.Frame(root)
#         self.custom_input_label = tk.Label(self.custom_input_frame, text="Enter custom number:", font=self.font_style)
#         self.custom_input_label.pack(side=tk.LEFT)
#
#         self.custom_input_entry = tk.Entry(self.custom_input_frame, font=self.font_style)
#         self.custom_input_entry.pack(side=tk.LEFT, padx=5)
#
#         self.apply_button = tk.Button(self.custom_input_frame, text="Apply", command=self.apply_custom_value, font=self.font_style)
#         self.apply_button.pack(side=tk.LEFT, padx=5)
#
#         # OK button to run analysis
#         self.ok_button = tk.Button(root, text="OK", command=self.run_analysis, font=self.font_style)
#         self.ok_button.pack(pady=20)
#
#     def select_excel_file(self):
#         """Allow the user to select an Excel file and store the path."""
#         file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls;*.xlsx")])
#         if file_path:  # Only update if a file was selected
#             self.selected_file = file_path
#             print(f"Selected file: {self.selected_file}")
#
#     def option_selected(self, value):
#         """Display custom input field if 'Custom' is selected."""
#         if value == "Custom" or "By time":
#             self.custom_input_frame.pack(pady=10)  # Show custom input frame
#         else:
#             self.custom_input_frame.pack_forget()  # Hide custom input frame
#
#     def time_selected(self, value):
#         """Display custom input field if 'Custom' is selected."""
#         if value == "By time":
#             self.radiobuttons_frame.pack(pady=10)  # Show custom input frame
#         else:
#             self.radiobuttons_frame.pack_forget()  # Hide custom input frame
#     def apply_custom_value(self):
#         """Retrieve the custom number and perform any action needed."""
#         custom_value = self.custom_input_entry.get()
#         if custom_value.isdigit():  # Simple check to ensure input is a number
#             print(f"Custom value applied: {custom_value}")
#         else:
#             messagebox.showerror("Invalid Input", "Please enter a valid number.")
#
#     def run_analysis(self):
#         """Run the analysis using the selected Excel file and display option."""
#         if self.selected_file:
#             display_option = self.display_option.get()
#             option_selected = self.option_var.get()
#             custom_value = self.custom_input_entry.get() if option_selected == "Custom" else None
#             # Placeholder for analysis code
#             print(f"Running analysis on {self.selected_file} with display option {display_option} and extra option {option_selected}")
#             if custom_value:
#                 print(f"Custom value used: {custom_value}")
#
#             # Notify user of completion
#             messagebox.showinfo("Analysis Complete", "The analysis has been completed. You can select a new file or change options.")
#         else:
#             messagebox.showwarning("No File Selected", "Please select an Excel file first.")
#
# # Example usage:
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = App(root)
#     root.mainloop()

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Analysis App")

        # Set window size and position
        window_width = 700
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Font style for widgets
        self.font_style = tkFont.Font(family="Helvetica", size=13)

        # Variable to track selected display option
        self.display_option = tk.StringVar(value='1')  # Default to 1

        # Radiobuttons frame
        self.radiobuttons_frame = tk.Frame(root)
        self.radiobuttons_frame.pack(pady=10)
        self.custom_input_label = tk.Label(self.radiobuttons_frame, text=" When to start counting the licks:", font=self.font_style)
        self.custom_input_label.pack(anchor=tk.W)
        # Radiobuttons with command to trigger display of entry field
        tk.Radiobutton(self.radiobuttons_frame, text="With stim", variable=self.display_option, value='1',
                       font=self.font_style, command=self.show_entry_field).pack(anchor=tk.W)
        tk.Radiobutton(self.radiobuttons_frame, text="After stim", variable=self.display_option, value='2',
                       font=self.font_style, command=self.show_entry_field).pack(anchor=tk.W)

        # Radiobutton with associated entry field
        self.bin_size_frame = tk.Frame(self.radiobuttons_frame)
        self.bin_size_radiobutton = tk.Radiobutton(self.bin_size_frame, text="By time",
                                                   variable=self.display_option, value='3',
                                                   font=self.font_style, command=self.show_entry_field)
        self.bin_size_radiobutton.pack(side=tk.LEFT)

        # Entry field for custom bin size (initially hidden)
        self.bin_size_entry = tk.Entry(self.bin_size_frame, font=self.font_style, width=5)
        self.bin_size_entry.pack(side=tk.LEFT, padx=5)
        self.bin_size_entry.pack_forget()  # Hide initially
        self.bin_size_frame.pack(anchor=tk.W)

###################################################################

        self.display_option2 = tk.StringVar(value='1')  # Default to 1

        # Radiobuttons frame
        self.radiobuttons_frame2 = tk.Frame(root)
        self.radiobuttons_frame2.pack(pady=10)
        self.custom_input_label2 = tk.Label(self.radiobuttons_frame2, text="Start trial:", font=self.font_style)
        self.custom_input_label2.pack(anchor=tk.W)
        # Radiobuttons with command to trigger display of entry field
        tk.Radiobutton(self.radiobuttons_frame2, text="Immediately", variable=self.display_option2, value='1',
                       font=self.font_style, command=self.show_entry_field2).pack(anchor=tk.W)

        # Radiobutton with associated entry field
        self.bin_size_frame2 = tk.Frame(self.radiobuttons_frame2)
        self.bin_size_radiobutton2 = tk.Radiobutton(self.bin_size_frame2, text="By time",
                                                   variable=self.display_option2, value='2',
                                                   font=self.font_style, command=self.show_entry_field2)
        self.bin_size_radiobutton2.pack(side=tk.LEFT)

        # Entry field for custom bin size (initially hidden)
        self.bin_size_entry2 = tk.Entry(self.bin_size_frame2, font=self.font_style, width=5)
        self.bin_size_entry2.pack(side=tk.LEFT, padx=5)
        self.bin_size_entry2.pack_forget()  # Hide initially
        self.bin_size_frame2.pack(anchor=tk.W)

 ##################################################################
        self.IR_no_RFID_frame = tk.Frame(root)
        self.custom_input_label3 = tk.Label(self.IR_no_RFID_frame, text="IR detected- no RFID:", font=self.font_style)
        self.custom_input_label3.pack(side=tk.LEFT)
        self.option_var = tk.StringVar(value="Take the Last RFID")  # Default value
        self.IR_no_RFID = ttk.OptionMenu(self.IR_no_RFID_frame, self.option_var, "Take the Last RFID", "Take the Last RFID", "dont start trial")
        self.IR_no_RFID.pack(pady=2,side=tk.LEFT)
        # Add IR_no_RFID_frame to the root window
        self.IR_no_RFID_frame.pack(pady=10)

####################################################################

        # Entry field for custom bin size (initially hidden)
        self.num_licks_frame = tk.Frame(root)
        self.num_licks_label = tk.Label(self.num_licks_frame, text="num of licks as response:", font=self.font_style)
        self.num_licks_label.pack(side=tk.LEFT)
        self.licks_entry = tk.Entry(self.num_licks_frame, font=self.font_style, width=5)
        self.licks_entry.pack(side=tk.LEFT, padx=10)
        self.num_licks_frame.pack(anchor=tk.W,pady=10)

#####################################################################

        # Entry field for custom bin size (initially hidden)
        self.ITI_frame = tk.Frame(root)
        self.ITI_label = tk.Label(self.ITI_frame, text="ITI:", font=self.font_style)
        self.ITI_label.pack(side=tk.LEFT)
        self.ITI_entry = tk.Entry(self.ITI_frame, font=self.font_style, width=5)
        self.ITI_entry.pack(side=tk.LEFT, padx=10)
        self.ITI_frame.pack(anchor=tk.W, pady=10)

#####################################################################

        # OK button to run analysis
        self.ok_button = tk.Button(root, text="OK", command=self.run_analysis, font=self.font_style)
        self.ok_button.pack(pady=20)
    
###################################################################
    def show_entry_field(self):
        """Show entry field only when 'By Bin Size' is selected."""
        if self.display_option.get() == '3':  # Show entry if "By Bin Size" is selected
            self.bin_size_entry.pack(side=tk.LEFT, padx=5)
        else:  # Hide entry for other options
            self.bin_size_entry.pack_forget()

    def show_entry_field2(self):
        """Show entry field only when 'By Bin Size' is selected."""
        if self.display_option2.get() == '2':  # Show entry if "By Bin Size" is selected
            self.bin_size_entry2.pack(side=tk.LEFT, padx=5)
        else:  # Hide entry for other options
            self.bin_size_entry2.pack_forget()

    def run_analysis(self):
        """Run analysis with selected options."""
        display_option = self.display_option.get()
        bin_size = self.bin_size_entry.get() if display_option == '3' else None

        # Here, you could insert code to use `display_option` and `bin_size` for analysis
        if bin_size:
            print(f"Running analysis with bin size: {bin_size}")
        else:
            print(f"Running analysis with option: {display_option}")


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
