import psutil
import os
import sys
import threading
import time
import subprocess

class MemoryMonitor:
    def __init__(self, experiment, threshold_mb=400, check_interval=60):
        """
        מערכת ניטור זיכרון אוטומטית
        experiment: אובייקט הניסוי
        threshold_mb: סף הזיכרון ב-MB שמעליו תתבצע אתחול מחדש
        check_interval: כמה שניות לבדוק בין בדיקות
        """
        self.experiment = experiment
        self.threshold_mb = threshold_mb
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """מתחיל את ניטור הזיכרון ברקע"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print(f"[MemoryMonitor] Memory monitoring started (threshold: {self.threshold_mb}MB)")
    
    def stop_monitoring(self):
        """עוצר את ניטור הזיכרון"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1)
            print("[MemoryMonitor] Memory monitoring stopped")
    
    def _monitor_loop(self):
        """לולאת הניטור הראשית"""
        while self.monitoring:
            try:
                current_memory = self._get_current_memory_mb()
                print(f"[MemoryMonitor] Memory usage {current_memory:.1f}MB , threshold {self.threshold_mb}MB")
                if current_memory > self.threshold_mb:
                    print(f"[MemoryMonitor] WARNING: Memory usage {current_memory:.1f}MB exceeds threshold {self.threshold_mb}MB")
                    self._handle_memory_overflow()
                    break  # יציאה מהלולאה אחרי הטיפול
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"[MemoryMonitor] Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _get_current_memory_mb(self):
        """מחזיר את השימוש הנוכחי בזיכרון ב-MB"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # המרה ל-MB
        except Exception as e:
            print(f"[MemoryMonitor] Error getting memory usage: {e}")
            return 0
    
    def _handle_memory_overflow(self):
        """מטפל בעליית הזיכרון מעל הסף"""
        try:
            print("[MemoryMonitor] Handling memory overflow - saving state and restarting...")
            
            # שמירת המצב הנוכחי
            self.experiment.save_minimal_state()
            
            # יצירת סקריפט אתחול מחדש
            restart_script = self._create_restart_script()
            
            # הפעלת הניסוי מחדש
            self._restart_experiment(restart_script)
            
        except Exception as e:
            print(f"[MemoryMonitor] Error during memory overflow handling: {e}")
    
    def _create_restart_script(self):
        """יוצר סקריפט Python שיאתחל מחדש את הניסוי"""
        try:
            # קבלת הנתיב המלא ל-experiment.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            experiment_path = os.path.join(current_dir, "experiment.py")
            
            script_content = f'''#!/usr/bin/env python3
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
experiment_path = "{experiment_path}"
if os.path.exists(experiment_path):
    print("[RestartScript] Found experiment.py at:", experiment_path)
else:
    print("[RestartScript] ERROR: experiment.py not found at:", experiment_path)
    sys.exit(1)

print("Restarting experiment automatically...")
print(f"Experiment name: {self.experiment.txt_file_name}")

# הפעלת הניסוי מחדש עם נתיב מלא
cmd = f'"{sys.executable}" "{experiment_path}" --restart {self.experiment.txt_file_name}'
print("[RestartScript] Running command:", cmd)

# שינוי לתיקייה הנכונה והפעלה
os.chdir(current_dir)
result = os.system(cmd)
print(f"[RestartScript] Command completed with result: {{result}}")
'''
            
            script_path = "restart_experiment.py"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # מתן הרשאות הרצה לסקריפט
            try:
                os.chmod(script_path, 0o755)
                print(f"[MemoryMonitor] Made script executable: {script_path}")
            except Exception as e:
                print(f"[MemoryMonitor] Warning: Could not make script executable: {e}")
            
            print(f"[MemoryMonitor] Restart script created: {script_path}")
            return script_path
            
        except Exception as e:
            print(f"[MemoryMonitor] Error creating restart script: {e}")
            return None
    
    def _restart_experiment(self, restart_script):
        """מאתחל מחדש את הניסוי"""
        try:
            print(f"[MemoryMonitor] Restarting experiment: {self.experiment.txt_file_name}")
            
            # הפעלת הסקריפט ברקע מאותה תיקייה
            if restart_script and os.path.exists(restart_script):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                restart_script_path = os.path.join(current_dir, restart_script)
                
                print(f"[MemoryMonitor] Spawning restart script: {restart_script_path}")
                print(f"[MemoryMonitor] Working directory: {current_dir}")
                
                # הפעלת הסקריפט עם subprocess במקום os.system
                process = subprocess.Popen([sys.executable, restart_script_path], 
                                        cwd=current_dir)
                
                # המתנה קצרה ואז יציאה
                time.sleep(1)
                print("[MemoryMonitor] Restart initiated, exiting current process...")
                
                # ניקוי משאבים לפני יציאה
                try:
                    if hasattr(self.experiment, 'live_w') and self.experiment.live_w:
                        try:
                            self.experiment.live_w.root.destroy()
                            time.sleep(0.1)
                        except:
                            pass
                except:
                    pass
                
                try:
                    if hasattr(self.experiment, 'root') and self.experiment.root:
                        try:
                            self.experiment.root.quit()
                            time.sleep(0.1)
                        except:
                            pass
                except:
                    pass
                
                # המתנה קטנה כדי לתת ל-GUI להסגר
                time.sleep(0.5)
                print("[MemoryMonitor] pre os.exist")
                if process.poll() is None:
                    print("Child started successfully")
                # יציאה מהתהליך הנוכחי
                sys.exit(0)#os._exit(0)
            else:
                print("[MemoryMonitor] Restart script not found, cannot restart")
                
        except Exception as e:
            print(f"[MemoryMonitor] Error during experiment restart: {e}")
            import traceback
            traceback.print_exc()
