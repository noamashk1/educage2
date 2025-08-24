#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט הפעלה מחדש של הניסוי עם המצב השמור
מתבצע אוטומטית כשהזיכרון עולה מעל 160MB
"""

import sys
import os
import json
import tkinter as tk
from tkinter import messagebox

# הוספת הנתיב הנוכחי ל-Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def load_saved_state():
    """טוען את המצב השמור מהקובץ"""
    state_file = "saved_experiment_state.json"
    
    if not os.path.exists(state_file):
        print(f"Error: Saved state file {state_file} not found")
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            saved_state = json.load(f)
        print(f"Loaded saved state for experiment: {saved_state.get('experiment_name', 'unknown')}")
        return saved_state
    except Exception as e:
        print(f"Error loading saved state: {e}")
        return None

def restore_mice_dict(saved_mice_dict):
    """משחזר את מילון העכברים מהמצב השמור"""
    try:
        from mouse import Mouse
        from level import Level
        
        restored_mice = {}
        for mouse_id, mouse_data in saved_mice_dict.items():
            # יצירת עכבר חדש
            mouse = Mouse(mouse_id)
            
            # שחזור הרמה
            if mouse_data.get('level'):
                level_data = mouse_data['level']
                level = Level(
                    level_data.get('level_number', 1),
                    level_data.get('stimulus_type', 'tone'),
                    level_data.get('stimulus_frequency', 10000),
                    level_data.get('stimulus_duration', 2.0)
                )
                mouse.update_level(level)
            
            # שחזור תוצאות
            if mouse_data.get('results'):
                mouse.results = mouse_data['results']
            
            restored_mice[mouse_id] = mouse
        
        print(f"Restored {len(restored_mice)} mice from saved state")
        return restored_mice
        
    except Exception as e:
        print(f"Error restoring mice dict: {e}")
        return {}

def restore_levels_df(saved_levels_df):
    """משחזר את טבלת הרמות מהמצב השמור"""
    try:
        from level import Level
        
        restored_levels = {}
        for level_num, level_data in saved_levels_df.items():
            level = Level(
                level_data.get('level_number', int(level_num)),
                level_data.get('stimulus_type', 'tone'),
                level_data.get('stimulus_frequency', 10000),
                level_data.get('stimulus_duration', 2.0)
            )
            restored_levels[level_num] = level
        
        print(f"Restored {len(restored_levels)} levels from saved state")
        return restored_levels
        
    except Exception as e:
        print(f"Error restoring levels: {e}")
        return {}

def show_restart_notification(experiment_name):
    """מציג הודעה על הפעלה מחדש"""
    root = tk.Tk()
    root.withdraw()  # מסתיר את החלון הראשי
    
    messagebox.showinfo(
        "System Restart", 
        f"המערכת הופעלה מחדש אוטומטית עקב שימוש גבוה בזיכרון.\n\n"
        f"הניסוי: {experiment_name}\n"
        f"המצב נשמר והמערכת חזרה לפעילות.\n\n"
        f"ניתן להמשיך בעבודה כרגיל."
    )
    
    root.destroy()

def main():
    """הפונקציה הראשית"""
    print("=== Experiment Restart Script ===")
    
    # טעינת המצב השמור
    saved_state = load_saved_state()
    if not saved_state:
        print("Failed to load saved state. Exiting.")
        return
    
    # הצגת הודעה על הפעלה מחדש
    experiment_name = saved_state.get('experiment_name', 'Unknown Experiment')
    show_restart_notification(experiment_name)
    
    # שחזור העכברים והרמות
    restored_mice = restore_mice_dict(saved_state.get('mice_dict', {}))
    restored_levels = restore_levels_df(saved_state.get('levels_df', {}))
    
    # יצירת הניסוי מחדש
    try:
        from experiment import Experiment
        
        print("Creating new experiment instance...")
        experiment = Experiment(
            exp_name=experiment_name,
            mice_dict=restored_mice,
            levels_df=restored_levels
        )
        
        # הגדרת הפרמטרים השמורים
        if saved_state.get('parameters'):
            experiment.set_parameters(saved_state['parameters'])
            print("Parameters restored from saved state")
        
        # הפעלת הניסוי
        print("Starting experiment...")
        experiment.run_experiment()
        
        # ניסיון לפתוח live_window אם היה פתוח
        if saved_state.get('gui_state', {}).get('live_window_open', False):
            print("Attempting to restore live_window...")
            try:
                # המתנה קצרה שהמערכת תתייצב
                import time
                time.sleep(2)
                
                # פתיחת live_window
                experiment.run_live_window()
                print("Live window restored successfully")
                
                # המתנה נוספת שהחלון ייפתח
                time.sleep(1)
                
            except Exception as e:
                print(f"Failed to restore live_window: {e}")
                # נסיון נוסף
                try:
                    print("Trying alternative method to open live_window...")
                    experiment.open_live_window()
                    print("Live window opened with alternative method")
                except Exception as e2:
                    print(f"Alternative method also failed: {e2}")
        
    except Exception as e:
        print(f"Error during experiment restart: {e}")
        messagebox.showerror(
            "Restart Error", 
            f"שגיאה בהפעלה מחדש של הניסוי:\n{str(e)}\n\n"
            "יש לבדוק את הלוגים ולנסות שוב."
        )

if __name__ == "__main__":
    main()
