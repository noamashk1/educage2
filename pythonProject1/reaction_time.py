# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.ndimage import gaussian_filter1d
# import matplotlib
# from datetime import datetime, timedelta
# import random
#
# matplotlib.use('TkAgg')
#
# # הגדרות
# BIN_SIZE_MS = 100
# TRIAL_DURATION_MS = 3000
# BIN_EDGES = np.arange(0, TRIAL_DURATION_MS + BIN_SIZE_MS, BIN_SIZE_MS)
# SMOOTH_SIGMA = 1
#
# # פורמט strftime עם מילישניות
# TIME_FORMAT = "%H:%M:%S.%f"
#
# # פונקציית עזר: ממירה רשימת זמנים בפורמט strftime למילישניות יחסית לראשון
# def convert_times_to_relative_ms(lick_time_strs):
#     times = [datetime.strptime(t, TIME_FORMAT) for t in lick_time_strs]
#     base_time = times[0]
#     return [int((t - base_time).total_seconds() * 1000) for t in times]
#
# # טוען קובץ שבו הזמנים הם בפורמט HH:MM:SS.sss
# def load_trials_labeled_strftime(file_path):
#     go_trials = []
#     nogo_trials = []
#
#     with open(file_path, 'r') as f:
#         for line in f:
#             if not line.strip():
#                 continue
#             label_part, times_part = line.strip().split("[")
#             label = label_part.strip().lower()
#             times_str = times_part.strip("[] \n")
#             lick_times = [t.strip() for t in times_str.split(",") if t.strip()]
#             if not lick_times:
#                 continue
#             rel_ms = convert_times_to_relative_ms(lick_times)
#             if label == "go":
#                 go_trials.append(rel_ms)
#             elif label == "no-go":
#                 nogo_trials.append(rel_ms)
#
#     return go_trials, nogo_trials
#
# # חישוב מטריצת בינים
# def compute_binned_matrix(trials, bin_edges):
#     return np.array([np.histogram(trial, bins=bin_edges)[0] for trial in trials])
#
# # ציור PSTH עם החלקה וסטיית תקן
# def plot_smoothed_psth(go_matrix, nogo_matrix, bin_edges):
#     time_axis = (bin_edges[:-1] + bin_edges[1:]) / 2
#
#     def compute_stats(matrix):
#         mean_vals = matrix.mean(axis=0)
#         stderr_vals = matrix.std(axis=0) / np.sqrt(matrix.shape[0])
#         return gaussian_filter1d(mean_vals, sigma=SMOOTH_SIGMA), gaussian_filter1d(stderr_vals, sigma=SMOOTH_SIGMA)
#
#     mean_go, stderr_go = compute_stats(go_matrix)
#     mean_nogo, stderr_nogo = compute_stats(nogo_matrix)
#
#     plt.figure(figsize=(10, 6))
#     plt.plot(time_axis, mean_go, label="Go", color='blue')
#     plt.fill_between(time_axis, mean_go - stderr_go, mean_go + stderr_go, color='blue', alpha=0.2)
#     plt.plot(time_axis, mean_nogo, label="No-Go", color='orange')
#     plt.fill_between(time_axis, mean_nogo - stderr_nogo, mean_nogo + stderr_nogo, color='orange', alpha=0.2)
#
#     plt.title("Smoothed PSTH of Licks (from stimulus)")
#     plt.xlabel("Time from Stimulus (ms)")
#     plt.ylabel("Average Licks per 100ms")
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()
#
# # יצירת דאטה בפורמט strftime
# def generate_strftime_data(num_trials=100, duration_ms=3000):
#     base_datetime = datetime.strptime("12:00:00.000", TIME_FORMAT)
#     data = []
#
#     for _ in range(num_trials):
#         label = "go" if random.random() < 0.6 else "no-go"
#         num_licks = random.randint(3, 8)
#         lick_offsets = sorted(random.sample(range(0, duration_ms), num_licks))  # במילישניות
#         lick_times = [(base_datetime + timedelta(milliseconds=ms)).strftime(TIME_FORMAT)[:-3] for ms in lick_offsets]
#         line = f"{label:<7}[{','.join(lick_times)}]"
#         data.append(line)
#
#     return data
#
# # שמירה לקובץ
# file_path = "C:\\Users\\noam4\\OneDrive\\Desktop\\lick_data_strftime.txt"
# demo_data = generate_strftime_data(100)
#
# with open(file_path, "w") as f:
#     for line in demo_data:
#         f.write(line + "\n")
#
# # טעינה, חישוב וציור
# go_trials, nogo_trials = load_trials_labeled_strftime(file_path)
# go_matrix = compute_binned_matrix(go_trials, BIN_EDGES)
# nogo_matrix = compute_binned_matrix(nogo_trials, BIN_EDGES)
# plot_smoothed_psth(go_matrix, nogo_matrix, BIN_EDGES)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from datetime import datetime
import ast

# הגדרות
BIN_SIZE_MS = 100
TRIAL_DURATION_MS = 3000
BIN_EDGES = np.arange(0, TRIAL_DURATION_MS + BIN_SIZE_MS, BIN_SIZE_MS)
SMOOTH_SIGMA = 1  # להחלקה של הגרף

def load_trials_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    go_trials = []
    nogo_trials = []

    for _, row in df.iterrows():
        label = row["go\\no-go"].strip().lower()
        start_time_str = row["start time"]
        licks_str = row["licks_time"]

        try:
            lick_times = ast.literal_eval(licks_str)
        except:
            continue

        if not lick_times:
            continue

        # חישוב זמנים יחסיים
        start_dt = datetime.strptime(start_time_str, "%H:%M:%S.%f")
        rel_licks = []
        for lick_str in lick_times:
            try:
                lick_dt = datetime.strptime(lick_str, "%H:%M:%S.%f")
                delta_ms = (lick_dt - start_dt).total_seconds() * 1000
                if 0 <= delta_ms <= TRIAL_DURATION_MS:
                    rel_licks.append(delta_ms)
            except:
                continue

        if label == "go":
            go_trials.append(rel_licks)
        elif label == "no-go":
            nogo_trials.append(rel_licks)

    return go_trials, nogo_trials

def compute_binned_matrix(trials, bin_edges):
    matrix = []
    for trial in trials:
        counts, _ = np.histogram(trial, bins=bin_edges)
        matrix.append(counts)
    return np.array(matrix)

def plot_smoothed_psth(go_matrix, nogo_matrix, bin_edges):
    time_axis = (bin_edges[:-1] + bin_edges[1:]) / 2

    def compute_stats(matrix):
        mean_vals = matrix.mean(axis=0)
        stderr_vals = matrix.std(axis=0) / np.sqrt(matrix.shape[0])
        return gaussian_filter1d(mean_vals, sigma=SMOOTH_SIGMA), gaussian_filter1d(stderr_vals, sigma=SMOOTH_SIGMA)

    mean_go, stderr_go = compute_stats(go_matrix)
    mean_nogo, stderr_nogo = compute_stats(nogo_matrix)

    plt.figure(figsize=(10, 6))
    plt.plot(time_axis, mean_go, label="Go", color='blue')
    plt.fill_between(time_axis, mean_go - stderr_go, mean_go + stderr_go, color='blue', alpha=0.3)
    plt.plot(time_axis, mean_nogo, label="No-Go", color='orange')
    plt.fill_between(time_axis, mean_nogo - stderr_nogo, mean_nogo + stderr_nogo, color='orange', alpha=0.3)

    plt.title("Smoothed PSTH of Licks (Go vs No-Go)")
    plt.xlabel("Time from Stimulus Onset (ms)")
    plt.ylabel("Average Licks per 100 ms")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# דוגמה לשימוש
csv_path = r"C:\Users\noam4\OneDrive\Desktop\lick_data_strftime.txt"  # שנה לשם הקובץ שלך
go_trials, nogo_trials = load_trials_from_csv(csv_path)
go_matrix = compute_binned_matrix(go_trials, BIN_EDGES)
nogo_matrix = compute_binned_matrix(nogo_trials, BIN_EDGES)
plot_smoothed_psth(go_matrix, nogo_matrix, BIN_EDGES)