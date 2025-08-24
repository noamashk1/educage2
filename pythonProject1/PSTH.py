import matplotlib
matplotlib.use("TkAgg")
import pandas as pd
import ast
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import ast
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
from tkinter import filedialog

# --- Tkinter GUI ---
root = tk.Tk()
root.title("Select Data File and Mouse")

# משתנה גלובלי לשמור את DataFrame
df = None
bin_size = 0.2
dur = 3

def compute_relative_licks(row):
    try:
        lick_list = ast.literal_eval(row["licks_time"])  # מחרוזת -> רשימה
        if not lick_list:
            return []

        start = datetime.strptime(row["start_time"], "%H:%M:%S.%f")
        rel = []
        for lick in lick_list:
            lick_time = datetime.strptime(lick, "%H:%M:%S.%f")
            rel.append((lick_time - start).total_seconds())
        return rel
    except Exception:
        return []

# פונקציה שממירה lick times לבינים
def assign_bins(rel_licks, bin_size=bin_size, max_time=dur):
    bins = []
    for t in rel_licks:
        if 0 <= t < max_time:
            bin_index = int(t / bin_size) + 1
            bins.append(bin_index)
    return bins


# פונקציה שמייצרת וקטור היסטוגרמה בגודל 30
def make_hist(rel_licks, bin_size=bin_size, max_time=dur):
    n_bins = int(max_time / bin_size)
    hist = np.zeros(n_bins, dtype=int)
    for t in rel_licks:
        if 0 <= t < max_time:
            idx = int(t / bin_size)
            hist[idx] += 1
    return hist.tolist()



def plot_psth_with_significance(mouse_id):
    mouse_df = df[df["mouse_ID"] == mouse_id]

    go_trials = mouse_df[mouse_df["go_no-go"] == "go"]
    nogo_trials = mouse_df[mouse_df["go_no-go"] == "no-go"]

    n_bins = int(dur/bin_size)
    # אם אין טריילים מסוג מסוים, יוצרים וקטור אפסים
    go_array = np.vstack(go_trials["lick_hist"].values) if not go_trials.empty else np.zeros((1, n_bins))
    nogo_array = np.vstack(nogo_trials["lick_hist"].values) if not nogo_trials.empty else np.zeros((1, n_bins))

    # ממוצע
    go_mean = go_array.mean(axis=0)
    nogo_mean = nogo_array.mean(axis=0)

    # t-test לכל bin
    p_values = []
    for bin_idx in range(n_bins):
        t_stat, p = ttest_ind(go_array[:, bin_idx], nogo_array[:, bin_idx])
        p_values.append(p)
    p_values = np.array(p_values)

    # Bonferroni correction
    _, p_corrected, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')

    # גרף
    bin_edges = np.arange(bin_size/2, dur, bin_size)
    plt.figure(figsize=(10, 5))
    plt.plot(bin_edges, go_mean, label="GO", color="green")
    plt.plot(bin_edges, nogo_mean, label="NO-GO", color="red")

    # סימון significance
    for i, p in enumerate(p_corrected):
        if p < 0.05:
            plt.text(bin_edges[i], max(go_mean[i], nogo_mean[i]) + 0.1, "*", ha='center', fontsize=10)

    plt.xlabel("Time since trial start (s)")
    plt.ylabel("Average lick count per bin")
    plt.title(f"PSTH for mouse {mouse_id} (Significant bins marked)")
    plt.legend()
    plt.tight_layout()
    plt.show()

def load_file():
    global df
    file_path = filedialog.askopenfilename(
        title="Select CSV/TXT file",
        filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if not file_path:
        return  # המשתמש ביטל את הבחירה

    # קריאת הקובץ
    df = pd.read_csv(file_path, names=[
        "date", "start_time", "end_time", "mouse_ID", "level",
        "go_no-go", "stim_index", "stim_name", "score", "licks_time"
    ])
    df_clean = df.tail(30000)  # או כל ניקוי אחר

    # הוספת עמודות relative_licks, lick_bins, lick_hist
    df["relative_licks"] = df.apply(compute_relative_licks, axis=1)
    df["lick_bins"] = df["relative_licks"].apply(assign_bins)
    df["lick_hist"] = df["relative_licks"].apply(make_hist)
    df["lick_hist"] = df["lick_hist"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # עדכון menu של העכברים
    mouse_ids = df["mouse_ID"].unique()
    selected_mouse.set(mouse_ids[0])
    mouse_menu['menu'].delete(0, 'end')
    for mid in mouse_ids:
        mouse_menu['menu'].add_command(label=mid, command=tk._setit(selected_mouse, mid))

# כפתור לבחירת הקובץ
file_button = ttk.Button(root, text="Load Data File", command=load_file)
file_button.pack(pady=10)

# תווית ובחירת העכבר
tk.Label(root, text="Choose mouse ID:").pack(pady=5)
selected_mouse = tk.StringVar(value="")
mouse_menu = ttk.OptionMenu(root, selected_mouse, "")
mouse_menu.pack(pady=5)

def on_plot_click():
    if df is not None and selected_mouse.get():
        plot_psth_with_significance(selected_mouse.get())

plot_button = ttk.Button(root, text="Plot PSTH", command=on_plot_click)
plot_button.pack(pady=10)

root.mainloop()



# import matplotlib
# matplotlib.use("TkAgg")
# import pandas as pd
# import ast
# from datetime import datetime
# import numpy as np
# import matplotlib.pyplot as plt
# import ast
# from datetime import datetime
# import tkinter as tk
# from tkinter import ttk
# from scipy.stats import ttest_ind
# from statsmodels.stats.multitest import multipletests
#
# path = r"C:\Users\noam4\OneDrive\Desktop\educage2\educage2\pythonProject1\experiments\all_test8.txt" #exp_03_08_2025\exp_03_08_2025.txt"
# # קריאת הקובץ עם שמות העמודות
# df = pd.read_csv(path, names=[
#     "date", "start_time", "end_time", "mouse_ID", "level",
#     "go_no-go", "stim_index", "stim_name", "score", "licks_time"
# ])
# print(df.size)
# df_clean = df.tail(30000)
#
# bin_size = 0.2
# dur = 3
#
# # פונקציה שמחשבת זמני ליקוקים יחסיים
# def compute_relative_licks(row):
#     try:
#         lick_list = ast.literal_eval(row["licks_time"])  # מחרוזת -> רשימה
#         if not lick_list:
#             return []
#
#         start = datetime.strptime(row["start_time"], "%H:%M:%S.%f")
#         rel = []
#         for lick in lick_list:
#             lick_time = datetime.strptime(lick, "%H:%M:%S.%f")
#             rel.append((lick_time - start).total_seconds())
#         return rel
#     except Exception:
#         return []
#
#
# # הוספת עמודת relative_licks
# df["relative_licks"] = df.apply(compute_relative_licks, axis=1)
#
#
# # פונקציה שממירה lick times לבינים
# def assign_bins(rel_licks, bin_size=bin_size, max_time=dur):
#     bins = []
#     for t in rel_licks:
#         if 0 <= t < max_time:
#             bin_index = int(t / bin_size) + 1
#             bins.append(bin_index)
#     return bins
#
#
# df["lick_bins"] = df["relative_licks"].apply(assign_bins)
#
#
# # פונקציה שמייצרת וקטור היסטוגרמה בגודל 30
# def make_hist(rel_licks, bin_size=bin_size, max_time=dur):
#     n_bins = int(max_time / bin_size)
#     hist = np.zeros(n_bins, dtype=int)
#     for t in rel_licks:
#         if 0 <= t < max_time:
#             idx = int(t / bin_size)
#             hist[idx] += 1
#     return hist.tolist()
#
#
# df["lick_hist"] = df["relative_licks"].apply(make_hist)
#
# # בדיקה
# print(df[["relative_licks", "lick_bins", "lick_hist"]].head())
# df.to_csv(r"C:\Users\noam4\OneDrive\Desktop\exp_03_08_2025_fix.txt", index=False)
#
# df["lick_hist"] = df["lick_hist"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
#
#
# def plot_psth_with_significance(mouse_id):
#     mouse_df = df[df["mouse_ID"] == mouse_id]
#
#     go_trials = mouse_df[mouse_df["go_no-go"] == "go"]
#     nogo_trials = mouse_df[mouse_df["go_no-go"] == "no-go"]
#
#     n_bins = int(dur/bin_size)
#     # אם אין טריילים מסוג מסוים, יוצרים וקטור אפסים
#     go_array = np.vstack(go_trials["lick_hist"].values) if not go_trials.empty else np.zeros((1, n_bins))
#     nogo_array = np.vstack(nogo_trials["lick_hist"].values) if not nogo_trials.empty else np.zeros((1, n_bins))
#
#     # ממוצע
#     go_mean = go_array.mean(axis=0)
#     nogo_mean = nogo_array.mean(axis=0)
#
#     # t-test לכל bin
#     p_values = []
#     for bin_idx in range(n_bins):
#         t_stat, p = ttest_ind(go_array[:, bin_idx], nogo_array[:, bin_idx])
#         p_values.append(p)
#     p_values = np.array(p_values)
#
#     # Bonferroni correction
#     _, p_corrected, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')
#
#     # גרף
#     bin_edges = np.arange(bin_size/2, dur, bin_size)
#     plt.figure(figsize=(10, 5))
#     plt.plot(bin_edges, go_mean, label="GO", color="green")
#     plt.plot(bin_edges, nogo_mean, label="NO-GO", color="red")
#
#     # סימון significance
#     for i, p in enumerate(p_corrected):
#         if p < 0.05:
#             plt.text(bin_edges[i], max(go_mean[i], nogo_mean[i]) + 0.1, "*", ha='center', fontsize=10)
#
#     plt.xlabel("Time since trial start (s)")
#     plt.ylabel("Average lick count per bin")
#     plt.title(f"PSTH for mouse {mouse_id} (Significant bins marked)")
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
#
#
# # --- Tkinter GUI ---
#
# root = tk.Tk()
# root.title("Select Mouse for PSTH")
#
# tk.Label(root, text="Choose mouse ID:").pack(pady=5)
#
# mouse_ids = df["mouse_ID"].unique()
# selected_mouse = tk.StringVar(value=mouse_ids[0])
#
# mouse_menu = ttk.OptionMenu(root, selected_mouse, mouse_ids[0], *mouse_ids)
# mouse_menu.pack(pady=5)
#
#
# def on_plot_click():
#     plot_psth_with_significance(selected_mouse.get())
#
#
# plot_button = ttk.Button(root, text="Plot PSTH", command=on_plot_click)
# plot_button.pack(pady=10)
#
# root.mainloop()
#
