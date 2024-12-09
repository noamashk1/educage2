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

def create_table(data_list, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    if data_list:
        # Style configuration
        label_font = ("Arial", 10)
        entry_font = ("Arial", 10)

        # Create headers for the columns
        tk.Label(frame, text="Mouse", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(frame, text="Level", font=("Arial", 12, "bold"), borderwidth=2).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

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



