#!/usr/bin/env python3
import sys
import os

# הוספת התיקייה הנוכחית ל-PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print("[RestartScript] CWD:", current_dir)
print("[RestartScript] Python:", sys.executable)
print("Restarting experiment automatically...")
print(f"Experiment name: exp_25_08_2025")

# הפעלת הניסוי מחדש עם אותו פרשן פייתון
cmd = f""/usr/bin/python3" experiment.py --restart exp_25_08_2025"
print("[RestartScript] Running:", cmd)
os.chdir(current_dir)
os.system(cmd)
