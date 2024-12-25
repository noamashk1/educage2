import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import pandas as pd
import csv
import mice_table_creating
import levels_table_creating
import parameters_GUI
#import experiment_1

class TkinterApp:
    def __init__(self, root,exp, exp_name):
        self.root = root
        self.root.title("Educage")
        #self.experiment = experiment_1.Experiment(exp_name, self.root)
        self.levels_list = []
        self.levels_df = None
        self.experiment = exp

        # Set the window dimensions
        w = 1200
        h = 800
        self.root.geometry(f"{w}x{h}")  # Adjust the size as needed

        # Create LabelFrames for the layout
        self.left_frame_top = tk.LabelFrame(root, text="Levels list", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        self.left_frame_middle = tk.LabelFrame(root, text="Mice list", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        self.left_frame_bottom = tk.LabelFrame(root, text="Parameters", font=("Helvetica", 12, "bold"), padx=10, pady=10)
        self.right_frame = tk.LabelFrame(root, text="Live window", font=("Helvetica", 12, "bold"), padx=10, pady=10)

        # Set the desired dimensions
        self.left_frame_top.config(width=w*(3/5), height=h/3)
        self.left_frame_middle.config(width=w*(3/5), height=h/3)
        self.left_frame_bottom.config(width=w*(3/5), height=h/3)
        self.right_frame.config(width=w*(2/5), height=h)

        # Prevent frames from resizing to fit their contents
        self.left_frame_top.pack_propagate(False)
        self.left_frame_middle.pack_propagate(False)
        self.left_frame_bottom.pack_propagate(False)
        self.right_frame.pack_propagate(False)

        # Place the frames in the window using grid
        self.left_frame_top.grid(row=0, column=0, sticky='nsew')
        self.left_frame_middle.grid(row=1, column=0, sticky='nsew')
        self.left_frame_bottom.grid(row=2, column=0, sticky='nsew')
        self.right_frame.grid(row=0, column=1, rowspan=3, sticky='nsew')

        # Configure row and column weights to make the layout responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Add widgets to the top left frame
        self.lvlBtnsFrame = tk.LabelFrame(self.left_frame_top)
        self.lvlBtnsFrame.grid(row=0, column=1, padx=10, pady=10)
        self.btnLoadLvl = tk.Button(self.lvlBtnsFrame, text="Load Levels", command=self.load_table)
        self.btnLoadLvl.grid(row=0, column=0, padx=10, pady=10)
        self.btnCreateLvl = tk.Button(self.lvlBtnsFrame, text="Create Levels", command=self.create_level_table)
        self.btnCreateLvl.grid(row=1, column=0, padx=10, pady=10)
        self.mice_table = mice_table_creating.MainApp(self.left_frame_middle, self)
        self.parameters_btns = parameters_GUI.ParametersApp(self.right_frame)
        self.ok_button = tk.Button(self.right_frame, text="OK", command=self.get_parameters)
        self.ok_button.pack(pady=20)

        ############# remove ######
        self.btnLoadLvl = tk.Button(self.left_frame_bottom, text="Load Levels", command=self.set_levels_df)
        self.btnLoadLvl.grid(row=0, column=0, padx=10, pady=10)


        # Create a Frame to hold the Treeview and Scrollbars
        self.tree_frame = tk.Frame(self.left_frame_top, width=600)
        self.tree_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.tree_frame.config(width=600, height=200)
        self.tree_frame.pack_propagate(False)

        # Prepare the Treeview in the tree frame
        self.tree = ttk.Treeview(self.tree_frame, columns=("Level Name","Stimulus Path", "Probability", "Value", "Index"), show='headings', height=5)
        self.tree.heading("Level Name", text="Level Name")
        self.tree.heading("Stimulus Path", text="Stimulus Path")
        self.tree.heading("Probability", text="Probability")
        self.tree.heading("Value", text="Value")
        self.tree.heading("Index", text="Index")


        # Set the width of the columns
        self.set_fixed_column_widths()
#         self.tree.column("Level Name",  width=50)
#         self.tree.column("Stimulus Path",  width=50)
#         self.tree.column("Probability",  width=50)
#         self.tree.column("Value", width=50)
#         self.tree.column("Index",  width=50)

        # Create vertical scrollbar
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.vsb.pack(side='right', fill='y')

        # Create horizontal scrollbar
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.hsb.pack(side='bottom', fill='x')

        # Configure the Treeview to use the scrollbars
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.tree.pack(pady=20, fill='both', expand=True)
        # Here you can set the maximum width for the Treeview:
        self.tree_frame.grid_propagate(False)  # Prevent the tree frame from resizing based on its contents

        # Configure the grid to expand
        self.left_frame_top.grid_columnconfigure(0, weight=1)  # Allow the Treeview
        self.left_frame_top.grid_columnconfigure(0, weight=1)  # Allow the Treeview to expand
        self.left_frame_top.grid_columnconfigure(1, weight=0)  # Button does not expand



    def create_level_table(self):
        #root = tk.Tk()
        levels_window = tk.Toplevel(self.root)
        level_definition_app = levels_table_creating.LevelDefinitionApp(levels_window)
        #levels_window = level_table2.LevelDefinitionApp(root)
        self.root.wait_window(levels_window)
        if level_definition_app.save_path:  # Ensure save_path is defined
            self.load_table(level_definition_app.save_path)
            self.update_level_list()
            self.set_levels_df()
            print("Loaded table with path:", level_definition_app.save_path)
        else:
            print("No save path defined.")
        self.load_table(level_definition_app.save_path)
        self.update_level_list()
        self.set_levels_df()
        

    def update_level_list(self):
        column_index = 0  # Index of the "level_name" column
        values = []
        # Retrieve values from the specified column
        for item in self.tree.get_children():
            item_values = self.tree.item(item)["values"]
            values.append(item_values[column_index])
        self.levels_list = sorted(list(set(values)))
        print("levels list:"+ str(self.levels_list))

    def load_table(self, file_path = None):
        if file_path == None:
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if not file_path:
            return  # User canceled the dialog
        try:
            # Clear existing data in the Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.tree["columns"] = []  # Clear existing columns
            self.tree["show"] = "headings"  # Show only headings, hide the first empty column

            # Check file extension
            if file_path.endswith('.csv'):
                # Load CSV
                with open(file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)  # Get the first row as header
                    # Dynamically create columns based on headers
                    self.tree["columns"] = headers
                    for header in headers:
                        self.tree.heading(header, text=header)  # Set headings
                    for row in reader:
                        self.tree.insert('', 'end', values=row)  # Insert data rows
            elif file_path.endswith('.xlsx'):
                # Load Excel file
                df = pd.read_excel(file_path)
                headers = df.columns.tolist()  # Get column headers from DataFrame
                # Dynamically create columns based on headers
                self.tree["columns"] = headers
                for header in headers:
                    self.tree.heading(header, text=header)  # Set headings
                for _, row in df.iterrows():
                    self.tree.insert('', 'end', values=row.tolist())  # Insert data rows
            else:
                messagebox.showerror("Error", "Unsupported file type.")
            self.update_level_list()
            self.set_levels_df()
            self.set_fixed_column_widths()
            self.clear_frame(self.left_frame_middle)                              ############## restart the mice if already chosen #####################
            self.mice_table = mice_table_creating.MainApp(self.left_frame_middle, self) ############## restart the mice if already chosen #####################
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def set_levels_df(self):
        # Retrieve the contents of the Treeview
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']  # Get the values of each item
            data.append(values)

        # Create a DataFrame from the list of values
        column_names = [self.tree.heading(col)['text'] for col in self.tree['columns']]
        self.levels_df = pd.DataFrame(data, columns=column_names)
        print(self.levels_df)

    def get_parameters(self):
        if self.levels_df is None:
            messagebox.showerror("Error", "You must set levels for the experiment.")

        elif self.mice_table.mice_dict == None:
            messagebox.showerror("Error", "You must update the mice table.")

        else:

            """Retrieve all user-selected parameters from the GUI."""
            parameters = {
                "display_option": self.parameters_btns.display_option.get(),
                "bin_size": self.parameters_btns.bin_size_entry.get() if self.parameters_btns.display_option.get() == '3' else None,
                # Add other options similarly, following the widget structure
                # For example:
                "start_trial_option": self.parameters_btns.display_option2.get(),
                "start_trial_time": self.parameters_btns.bin_size_entry2.get() if self.parameters_btns.display_option2.get() == '2' else None,
                "IR_no_RFID_option": self.parameters_btns.option_var.get(),
                "lick_threshold": self.parameters_btns.licks_entry.get(),
                "ITI": self.parameters_btns.ITI_display_option.get(),
                "ITI_time": self.parameters_btns.ITI_bin_size_entry.get() if self.parameters_btns.ITI_display_option.get() == '2' else None,
            }
            # Set parameters in the Experiment class
            self.experiment.set_levels_df(self.levels_df)
            self.mice_table.set_mice_as_dict()
            self.experiment.set_mice_dict(self.mice_table.mice_dict)
            self.experiment.set_parameters(parameters)
    
    def set_fixed_column_widths(self):
        # Define fixed widths for the columns
        self.tree.column("Level Name", width=50)
        self.tree.column("Stimulus Path", width=200)
        self.tree.column("Probability", width=50)
        self.tree.column("Value", width=50)
        self.tree.column("Index", width=50)


# # Main code to run the app
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TkinterApp(root)
#     root.mainloop()