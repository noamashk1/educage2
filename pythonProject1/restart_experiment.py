#!/usr/bin/env python3
import sys
import os

# הוספת התיקייה הנוכחית ל-PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# הפעלת הניסוי מחדש
os.system(f"python experiment.py --restart try_reatart_25_08_2025")
