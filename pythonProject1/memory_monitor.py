import psutil
import threading
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class MemoryMonitor:
    """
    מערכת ניטור זיכרון שמאתחלת את המערכת אוטומטית כשהזיכרון עולה מעל 160MB
    שומרת את המצב הנוכחי ומחזירה את המערכת למצב פעיל
    """
    
    def __init__(self, experiment_instance, memory_threshold_mb: int = 150, check_interval: float = 15):
        self.experiment = experiment_instance
        self.memory_threshold_mb = memory_threshold_mb
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # שמירת המצב הנוכחי
        self.saved_state = {}
        self.state_file = "saved_experiment_state.json"
        
        print(f"[MemoryMonitor] Initialized with threshold: {memory_threshold_mb}MB")
    
    def start_monitoring(self):
        """מתחיל את ניטור הזיכרון"""
        if self.is_monitoring:
            print("[MemoryMonitor] Already monitoring")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[MemoryMonitor] Memory monitoring started")
    
    def stop_monitoring(self):
        """עוצר את ניטור הזיכרון"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            try:
                # בדיקה אם זה ה-thread הנוכחי
                if self.monitor_thread == threading.current_thread():
                    print("[MemoryMonitor] Cannot join current thread, continuing...")
                else:
                    self.monitor_thread.join(timeout=2.0)
            except Exception as e:
                print(f"[MemoryMonitor] Error stopping monitoring: {e}")
        print("[MemoryMonitor] Memory monitoring stopped")
    
    def _monitor_loop(self):
        """לולאת הניטור הראשית"""
        while self.is_monitoring:
            try:
                current_memory = self._get_current_memory_mb()
                
                if current_memory > self.memory_threshold_mb:
                    print(f"[MemoryMonitor] WARNING: Memory usage {current_memory:.1f}MB exceeds threshold {self.memory_threshold_mb}MB")
                    # בדיקה שהתהליך עדיין פעיל
                    if hasattr(self.experiment, 'root') and self.experiment.root:
                        try:
                            # בדיקה שהחלון עדיין פעיל
                            self.experiment.root.winfo_exists()
                            self._handle_memory_overflow()
                            # יציאה מהלולאה אחרי הטיפול
                            break
                        except Exception as e:
                            print(f"[MemoryMonitor] Window no longer exists, stopping monitoring: {e}")
                            self.is_monitoring = False
                            break
                    else:
                        print("[MemoryMonitor] Experiment no longer exists, stopping monitoring")
                        self.is_monitoring = False
                        break
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"[MemoryMonitor] Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _get_current_memory_mb(self) -> float:
        """מחזיר את השימוש הנוכחי בזיכרון ב-MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)
        except Exception as e:
            print(f"[MemoryMonitor] Error getting memory info: {e}")
            return 0.0
    
    def _handle_memory_overflow(self):
        """מטפל בעליית הזיכרון מעל הסף - שומר מצב ומאתחל"""
        print(f"[MemoryMonitor] Handling memory overflow - saving state and restarting...")
        
        try:
            # שמירת המצב הנוכחי
            self._save_current_state()
            
            # עצירת הניטור הנוכחי
            self.stop_monitoring()
            
            # אתחול המערכת
            self._restart_system()
            
        except Exception as e:
            print(f"[MemoryMonitor] Error during memory overflow handling: {e}")
            # נסיון לשמור מצב בסיסי
            try:
                self._save_basic_state()
            except Exception as e2:
                print(f"[MemoryMonitor] Failed to save even basic state: {e2}")
    
    def _save_current_state(self):
        """שומר את המצב הנוכחי של הניסוי"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'experiment_name': getattr(self.experiment, 'txt_file_name', 'unknown'),
                'parameters': self._serialize_parameters(),
                'mice_dict': self._serialize_mice_dict(),
                'levels_df': self._serialize_levels_df(),
                'fsm_state': self._get_fsm_state(),
                'gui_state': self._get_gui_state()
            }
            
            # בדיקה שהמצב ניתן לשמירה
            try:
                # בדיקה שהמצב ניתן להמרה ל-JSON
                json.dumps(state, ensure_ascii=False)
            except Exception as e:
                print(f"[MemoryMonitor] State contains non-serializable objects: {e}")
                # ניקוי המצב מאובייקטים לא ניתנים לשמירה
                state = self._clean_state_for_json(state)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            print(f"[MemoryMonitor] State saved to {self.state_file}")
            
        except Exception as e:
            print(f"[MemoryMonitor] Error saving state: {e}")
            # נסיון לשמור מצב בסיסי
            try:
                self._save_basic_state()
            except Exception as e2:
                print(f"[MemoryMonitor] Failed to save even basic state: {e2}")
    
    def _serialize_parameters(self):
        """ממיר פרמטרים לפורמט שניתן לשמור"""
        try:
            params = getattr(self.experiment, 'exp_params', {})
            if params is None:
                return {}
            
            # המרה לפורמט JSON
            serialized = {}
            for key, value in params.items():
                try:
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        serialized[key] = value
                    elif hasattr(value, 'to_dict'):  # DataFrame
                        serialized[key] = value.to_dict()
                    elif hasattr(value, '__dict__'):  # אובייקט
                        serialized[key] = str(value)
                    else:
                        # המרה למחרוזת אם לא ניתן לשמור
                        serialized[key] = str(value)
                except Exception as e:
                    print(f"[MemoryMonitor] Error serializing parameter {key}: {e}")
                    serialized[key] = f"ERROR: {str(value)}"
            
            return serialized
        except Exception as e:
            print(f"[MemoryMonitor] Error serializing parameters: {e}")
            return {}
    
    def _serialize_levels_df(self):
        """ממיר את טבלת הרמות לפורמט שניתן לשמור"""
        try:
            levels_df = getattr(self.experiment, 'levels_df', {})
            if levels_df is None or levels_df == {}:
                return {}
            
            # בדיקה אם זה DataFrame
            if hasattr(levels_df, 'empty'):
                # זה DataFrame - המרה לפורמט שניתן לשמור
                try:
                    # ניסיון המרה בטוחה
                    if levels_df.empty:
                        return []
                    else:
                        return levels_df.to_dict('records')
                except Exception as e:
                    print(f"[MemoryMonitor] Error converting DataFrame to dict: {e}")
                    # נסיון המרה פשוטה יותר
                    try:
                        return levels_df.values.tolist()
                    except Exception as e2:
                        print(f"[MemoryMonitor] Failed alternative DataFrame conversion: {e2}")
                        return []
            
            # אם זה מילון רגיל
            serialized = {}
            for level_num, level in levels_df.items():
                try:
                    if hasattr(level, '__dict__'):
                        # המרה של אובייקט Level
                        level_data = {}
                        for attr, value in level.__dict__.items():
                            if isinstance(value, (str, int, float, bool, list, dict)):
                                level_data[attr] = value
                            elif hasattr(value, 'to_dict'):  # DataFrame
                                try:
                                    level_data[attr] = value.to_dict()
                                except Exception as e:
                                    level_data[attr] = str(value)
                            else:
                                level_data[attr] = str(value)
                        serialized[str(level_num)] = level_data
                    elif hasattr(level, 'to_dict'):  # DataFrame
                        try:
                            serialized[str(level_num)] = level.to_dict()
                        except Exception as e:
                            serialized[str(level_num)] = str(level)
                    else:
                        # אם זה כבר מילון או משהו אחר
                        serialized[str(level_num)] = str(level)
                except Exception as e:
                    print(f"[MemoryMonitor] Error serializing level {level_num}: {e}")
                    serialized[str(level_num)] = f"ERROR: {str(level)}"
            
            return serialized
        except Exception as e:
            print(f"[MemoryMonitor] Error serializing levels: {e}")
            return {}
    
    def _clean_state_for_json(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """מנקה את המצב מאובייקטים לא ניתנים לשמירה ב-JSON"""
        try:
            cleaned_state = {}
            for key, value in state.items():
                try:
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        cleaned_state[key] = value
                    elif hasattr(value, '__dict__'):
                        # אובייקט - המרה למחרוזת
                        cleaned_state[key] = str(value)
                    else:
                        # אחר - המרה למחרוזת
                        cleaned_state[key] = str(value)
                except Exception as e:
                    print(f"[MemoryMonitor] Error cleaning state key {key}: {e}")
                    cleaned_state[key] = f"ERROR: {str(value)}"
            
            return cleaned_state
        except Exception as e:
            print(f"[MemoryMonitor] Error cleaning state: {e}")
            return {'error': 'Failed to clean state', 'timestamp': datetime.now().isoformat()}
    
    def _serialize_mice_dict(self) -> Dict[str, Any]:
        """ממיר את מילון העכברים לפורמט שניתן לשמור"""
        try:
            mice_data = {}
            if hasattr(self.experiment, 'mice_dict') and self.experiment.mice_dict:
                for mouse_id, mouse in self.experiment.mice_dict.items():
                    mice_data[mouse_id] = {
                        'id': mouse_id,
                        'level': getattr(mouse, 'level', {}),
                        'results': getattr(mouse, 'results', [])
                    }
            return mice_data
        except Exception as e:
            print(f"[MemoryMonitor] Error serializing mice dict: {e}")
            return {}
    
    def _get_fsm_state(self) -> Dict[str, Any]:
        """מחזיר את המצב הנוכחי של ה-FSM"""
        try:
            if hasattr(self.experiment, 'fsm') and self.experiment.fsm:
                return {
                    'current_state': getattr(self.experiment.fsm, 'current_state', 'unknown'),
                    'trial_count': getattr(self.experiment.fsm, 'trial_count', 0),
                    'active_mouse': getattr(self.experiment.fsm, 'active_mouse', None)
                }
            return {}
        except Exception as e:
            print(f"[MemoryMonitor] Error getting FSM state: {e}")
            return {}
    
    def _get_gui_state(self) -> Dict[str, Any]:
        """מחזיר את המצב הנוכחי של ה-GUI"""
        try:
            gui_state = {}
            
            if hasattr(self.experiment, 'GUI'):
                gui_state['window_geometry'] = getattr(self.experiment.GUI, 'root', {}).geometry() if hasattr(self.experiment.GUI, 'root') else ''
                gui_state['live_window_open'] = hasattr(self.experiment, 'live_w') and self.experiment.live_w is not None
                
                # שמירת מידע נוסף על live_window
                if hasattr(self.experiment, 'live_w') and self.experiment.live_w is not None:
                    try:
                        live_w = self.experiment.live_w
                        # המרה בטוחה של ערכי tkinter
                        last_rfid = getattr(live_w, 'last_rfid_value', None)
                        if last_rfid is not None:
                            try:
                                # ניסיון לקבל את הטקסט מהאובייקט
                                if hasattr(last_rfid, 'cget'):
                                    last_rfid_text = last_rfid.cget('text')
                                elif hasattr(last_rfid, 'get'):
                                    last_rfid_text = last_rfid.get()
                                else:
                                    last_rfid_text = str(last_rfid)
                            except Exception as e:
                                last_rfid_text = str(last_rfid)
                        else:
                            last_rfid_text = None
                        
                        gui_state['live_window_info'] = {
                            'is_open': True,
                            'last_rfid': last_rfid_text,
                            'window_geometry': getattr(live_w, 'root', {}).geometry() if hasattr(live_w, 'root') else ''
                        }
                    except Exception as e:
                        print(f"[MemoryMonitor] Error getting live_window info: {e}")
                        gui_state['live_window_info'] = {'is_open': True, 'error': str(e)}
                else:
                    gui_state['live_window_info'] = {'is_open': False}
            
            return gui_state
        except Exception as e:
            print(f"[MemoryMonitor] Error getting GUI state: {e}")
            return {}
    
    def _restart_system(self):
        """מאתחל את המערכת עם המצב השמור"""
        try:
            print("[MemoryMonitor] Restarting system...")
            
            # עצירת התהליך הנוכחי בצורה בטוחה
            if hasattr(self.experiment, 'root') and self.experiment.root:
                try:
                    # ניסיון לסגור את החלונות בצורה בטוחה
                    if hasattr(self.experiment, 'live_w') and self.experiment.live_w is not None:
                        try:
                            self.experiment.live_w.root.destroy()
                        except Exception as e:
                            print(f"[MemoryMonitor] Error closing live_window: {e}")
                    
                    # עצירת ה-GUI הראשי
                    self.experiment.root.quit()
                except Exception as e:
                    print(f"[MemoryMonitor] Error stopping GUI: {e}")
            
            # הפעלה מחדש עם המצב השמור
            self._restart_experiment()
            
        except Exception as e:
            print(f"[MemoryMonitor] Error during restart: {e}")
    
    def _restart_experiment(self):
        """מפעיל מחדש את הניסוי עם המצב השמור"""
        try:
            # קריאת המצב השמור
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    saved_state = json.load(f)
                
                print(f"[MemoryMonitor] Restarting experiment: {saved_state.get('experiment_name', 'unknown')}")
                
                # הפעלה מחדש של הניסוי עם הפרמטרים השמורים
                self._create_restart_script(saved_state)
                
            else:
                print("[MemoryMonitor] No saved state found, cannot restart")
                
        except Exception as e:
            print(f"[MemoryMonitor] Error during experiment restart: {e}")
    
    def _create_restart_script(self, saved_state: Dict[str, Any]):
        """יוצר סקריפט הפעלה מחדש"""
        try:
            restart_script = f"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from experiment import Experiment
import json

# קריאת המצב השמור
with open('{self.state_file}', 'r', encoding='utf-8') as f:
    saved_state = json.load(f)

# יצירת הניסוי מחדש עם הפרמטרים השמורים
experiment = Experiment(
    exp_name=saved_state['experiment_name'],
    mice_dict=saved_state.get('mice_dict', {{}}),
    levels_df=saved_state.get('levels_df', {{}})
)

# הגדרת הפרמטרים השמורים
if saved_state.get('parameters'):
    experiment.set_parameters(saved_state['parameters'])

# הפעלת הניסוי
experiment.run_experiment()
"""
            
            with open('restart_experiment.py', 'w', encoding='utf-8') as f:
                f.write(restart_script)
            
            print("[MemoryMonitor] Restart script created: restart_experiment.py")
            
            # הפעלת הסקריפט
            import sys
            os.system(f"{sys.executable} restart_experiment.py")
            
        except Exception as e:
            print(f"[MemoryMonitor] Error creating restart script: {e}")
    
    def _save_basic_state(self):
        """שומר מצב בסיסי בלבד - רק מה שניתן לשמור בוודאות"""
        try:
            basic_state = {
                'timestamp': datetime.now().isoformat(),
                'experiment_name': getattr(self.experiment, 'txt_file_name', 'unknown'),
                'error': 'Full state save failed, saved basic info only'
            }
            
            basic_file = "basic_experiment_state.json"
            with open(basic_file, 'w', encoding='utf-8') as f:
                json.dump(basic_state, f, indent=2, ensure_ascii=False)
            
            print(f"[MemoryMonitor] Basic state saved to {basic_file}")
            
        except Exception as e:
            print(f"[MemoryMonitor] Failed to save basic state: {e}")
    
    def get_memory_usage(self) -> float:
        """מחזיר את השימוש הנוכחי בזיכרון ב-MB"""
        return self._get_current_memory_mb()
    
    def get_memory_status(self) -> Dict[str, Any]:
        """מחזיר מידע על מצב הזיכרון"""
        current_memory = self._get_current_memory_mb()
        return {
            'current_memory_mb': current_memory,
            'threshold_mb': self.memory_threshold_mb,
            'is_over_threshold': current_memory > self.memory_threshold_mb,
            'is_monitoring': self.is_monitoring
        }


# פונקציה עזר לבדיקת זיכרון
def check_memory_usage() -> float:
    """בודק את השימוש בזיכרון של התהליך הנוכחי"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return memory_info.rss / (1024 * 1024)
    except Exception:
        return 0.0


if __name__ == "__main__":
    # בדיקה פשוטה
    print(f"Current memory usage: {check_memory_usage():.1f} MB")
