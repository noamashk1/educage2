#!/usr/bin/env python3
import sys
import os

print("[RestartScript] Starting restart process...")
print("[RestartScript] Current working directory:", os.getcwd())

# Adding the current directory to PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print("[RestartScript] Script directory:", current_dir)
print("[RestartScript] Python interpreter:", sys.executable)

# Checking if experiment.py exists
experiment_path = "/home/educage/projects/educage2/experiment.py"
if os.path.exists(experiment_path):
    print("[RestartScript] Found experiment.py at:", experiment_path)
else:
    print("[RestartScript] ERROR: experiment.py not found at:", experiment_path)
    sys.exit(1)

print("Restarting experiment automatically...")
print(f"Experiment name: asd_juv_30_06_2026")

# Running the experiment with full path
cmd = f'"/home/educage/projects/educage2/venv/bin/python3.13" "/home/educage/projects/educage2/experiment.py" --restart asd_juv_30_06_2026'
print("[RestartScript] Running command:", cmd)

# Changing to the correct directory and running
os.chdir(current_dir)
result = os.system(cmd)
print(f"[RestartScript] Command completed with result: {result}")
