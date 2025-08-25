#!/usr/bin/env python3
import sys
import os

print("[RestartScript] Starting restart process...")
print("[RestartScript] Current working directory:", os.getcwd())

# הוספת התיקייה הנוכחית ל-PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print("[RestartScript] Script directory:", current_dir)
print("[RestartScript] Python interpreter:", sys.executable)

# בדיקה שה-experiment.py קיים
experiment_path = "/home/educage/git_educage2/educage2/pythonProject1/experiment.py"
if os.path.exists(experiment_path):
    print("[RestartScript] Found experiment.py at:", experiment_path)
else:
    print("[RestartScript] ERROR: experiment.py not found at:", experiment_path)
    sys.exit(1)

print("Restarting experiment automatically...")
print(f"Experiment name: exp_25_08_2025")

# הפעלת הניסוי מחדש עם נתיב מלא
cmd = f'"/usr/bin/python3" "/home/educage/git_educage2/educage2/pythonProject1/experiment.py" --restart exp_25_08_2025'
print("[RestartScript] Running command:", cmd)

# שינוי לתיקייה הנכונה והפעלה
os.chdir(current_dir)
result = os.system(cmd)
print(f"[RestartScript] Command completed with result: {result}")
