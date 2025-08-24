import psutil
import numpy as np
import time
import sounddevice as sd
import os
from datetime import datetime

process = psutil.Process(os.getpid())
path = '/home/educage/git_educage2/educage2/pythonProject1/stimuli/14KHZ.npz'
data = np.load(path)
stim = data['data']
fs = int(data['rate'])

LOG_FILE = "debug_simulation_log.txt"

def log_memory_usage(tag=""):
    """Log current memory usage in MB."""
    mem = process.memory_info().rss / (1024 * 1024)  # in MB
    log_message(f"[MEM] {tag} Memory usage: {mem:.2f} MB")
def log_message(message: str):
    """Write message to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
        
minutes_passed = 0  
last_log_time = time.time()
while True:
    if time.time() - last_log_time > 60:
        minutes_passed += 1
        last_log_time = time.time()
        print(f"{minutes_passed} minutes passed")
    sd.play(stim, samplerate=fs)#, blocking=True
    time.sleep(0.5)
    sd.stop()
    time.sleep(0.2)
    if minutes_passed%5 == 0:
        log_memory_usage("sound simulation")