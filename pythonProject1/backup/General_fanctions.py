import tkinter as tk
def center_the_window(window,size=None):
    # Implicitly set dimensions for example purposes
    if size is not None:
        window.geometry(size)
    
    # Ensures the window's dimensions are known
    window.update_idletasks()

    # Retrieve the window size dynamically
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the center position
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    
    # Adjust the window's position to be centered
    window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
#     
# def create_table(data_list,frame):
#     for widget in frame.winfo_children():
#         widget.destroy()
# 
#     if not data_list:
#         data_list =[""]
# #     # Create a LabelFrame to act as a container for the table
# #     frame = tk.LabelFrame(root, text="Mice List", font=("Arial", 12, "bold"), padx=10, pady=10)
# #     frame.pack(padx=10, pady=10, fill="both", expand=True)
# 
#     # Style configuration
#     label_font = ("Arial", 10)
#     entry_font = ("Arial", 10)
# 
#     # Create headers for the columns
#     tk.Label(frame, text="Mouse", font=("Arial", 12, "bold"), borderwidth=1, relief="solid").grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
#     tk.Label(frame, text="Level", font=("Arial", 12, "bold"), borderwidth=1, relief="solid").grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
# 
#     # Populate the table
#     for i, item in enumerate(data_list):
#         # Create a label for each list item with border
#         label = tk.Label(frame, text=item, font=label_font, borderwidth=1, relief="solid")
#         label.grid(row=i + 1, column=0, sticky="nsew", padx=1, pady=1)
# 
#         # Create an entry field with default value '1' for user input with border
#         entry = tk.Entry(frame, font=entry_font, borderwidth=1, relief="solid")
#         entry.insert(0, "1")  # Insert default value of '1'
#         entry.grid(row=i + 1, column=1, sticky="nsew", padx=1, pady=1)
# 
#     # Configure grid size weights for uniformity
#     for col in range(2):  # Two columns: "List Item" and " User Input"
#         frame.grid_columnconfigure(col, weight=1)
#     for row in range(len(data_list) + 1):
#         frame.grid_rowconfigure(row, weight=1)
#         
# def create_table(data_list,frame):
#     for widget in frame.winfo_children():
#         widget.destroy()
# 
#     if data_list:
# #     # Create a LabelFrame to act as a container for the table
# #     frame = tk.LabelFrame(root, text="Mice List", font=("Arial", 12, "bold"), padx=10, pady=10)
# #     frame.pack(padx=10, pady=10, fill="both", expand=True)
# 
#     # Style configuration
#         label_font = ("Arial", 10)
#         entry_font = ("Arial", 10)
# 
#         # Create headers for the columns
#         tk.Label(frame, text="Mouse", font=("Arial", 12, "bold"), borderwidth=1, relief="solid").grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
#         tk.Label(frame, text="Level", font=("Arial", 12, "bold"), borderwidth=1, relief="solid").grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
# 
#         # Populate the table
#         for i, item in enumerate(data_list):
#             # Create a label for each list item with border
#             label = tk.Label(frame, text=item, font=label_font, borderwidth=1, relief="solid")
#             label.grid(row=i + 1, column=0, sticky="nsew", padx=1, pady=1)
# 
#             # Create an entry field with default value '1' for user input with border
#             entry = tk.Entry(frame, font=entry_font, borderwidth=1, relief="solid")
#             entry.insert(0, "1")  # Insert default value of '1'
#             entry.grid(row=i + 1, column=1, sticky="nsew", padx=1, pady=1)
# 
#         # Configure grid size weights for uniformity
#         for col in range(2):  # Two columns: "List Item" and " User Input"
#             frame.grid_columnconfigure(col, weight=1)
#         for row in range(len(data_list) + 1):
#             frame.grid_rowconfigure(row, weight=1)



def create_table(data_list, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    if data_list:
        # Style configuration
        label_font = ("Arial", 10)
        entry_font = ("Arial", 10)

        # Create headers for the columns
        tk.Label(frame, text="Mouse", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        tk.Label(frame, text="Level", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Populate the table
        for i, item in enumerate(data_list):
            # Create a label for each list item
            label = tk.Label(frame, text=item, font=label_font, borderwidth=0)
            label.grid(row=i + 1, column=0, sticky="nsew", padx=5, pady=2)

            # Create an entry field with default value '1' for user input
            entry = tk.Entry(frame, font=entry_font, width=5, borderwidth=0)
            entry.insert(0, "1")  # Insert default value of '1'
            entry.grid(row=i + 1, column=1, sticky="nsew", padx=5, pady=2)

        # Configure grid size weights for uniformity
        frame.grid_columnconfigure(0, weight=1)  # Mouse column
        frame.grid_columnconfigure(1, weight=0)  # Level column, keeping it narrower
        for row in range(len(data_list) + 1):
            frame.grid_rowconfigure(row, weight=0)  # No expansion for rows to keep height small



