import os
import time
import numpy as np
import sounddevice as sd

# Previous default playback (kept as comment):
# try:
#     with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/white_noise.npz', mmap_mode='r') as z:
#          noise = z['noise']
#          Fs = int(z['Fs'])
#     sd.play(noise, samplerate=Fs, blocking=True)  #sd.wait()
# finally:
#     sd.stop()
#     time.sleep(1)
# try:
#     with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise_with_ultrasonic.npz', mmap_mode='r') as z:
#          noise = z['data']
#          Fs = int(z['Fs'])
#     sd.play(noise, samplerate=Fs, blocking=True)
# finally:
#     sd.stop()
#     time.sleep(1)
# try:
#     with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise.npz', mmap_mode='r') as z:
#          noise = z['data']
#          Fs = int(z['Fs'])
#     sd.play(noise, samplerate=Fs, blocking=True)
# finally:
#     sd.stop()
#     time.sleep(1)
# try:
#     with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise_with_ultrasonic.npz', mmap_mode='r') as z:
#          noise = z['data']
#          Fs = int(z['Fs'])
#     sd.play(noise, samplerate=Fs)
#     sd.wait()
# finally:
#     sd.stop()
#     time.sleep(1)
# try:
#     with np.load('/home/educage/git_educage2/educage2/pythonProject1/stimuli/scary_noise.npz', mmap_mode='r') as z:
#          noise = z['data']
#          Fs = int(z['Fs'])
#     sd.play(noise, samplerate=Fs)
#     sd.wait()
# finally:
#     sd.stop()
#     time.sleep(1)


def play_npz_stim(stim_name: str):
    stim_path = os.path.join(os.getcwd(), "stimuli", f"{stim_name}.npz")
    with np.load(stim_path, mmap_mode="r") as z:
        if "data" in z:
            signal = z["data"]
        elif "noise" in z:
            signal = z["noise"]
        else:
            signal = z[z.files[0]]

        if "rate" in z:
            fs = int(z["rate"])
        elif "Fs" in z:
            fs = int(z["Fs"])
        else:
            raise KeyError(f"No sample-rate key ('rate'/'Fs') in {stim_path}")

    sd.play(signal, samplerate=fs, blocking=True)
    sd.stop()
    time.sleep(1)


for stim in ["7-07", "9-17", "10-95", "14-14","scary_noise"]:
    play_npz_stim(stim)
