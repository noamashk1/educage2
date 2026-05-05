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
            signal = np.array(z["data"], dtype=np.float32, copy=True)
        elif "noise" in z:
            signal = np.array(z["noise"], dtype=np.float32, copy=True)
        else:
            signal = np.array(z[z.files[0]], dtype=np.float32, copy=True)

        if "rate" in z:
            fs = int(z["rate"].item()) if hasattr(z["rate"], "item") else int(z["rate"])
        elif "Fs" in z:
            fs = int(z["Fs"].item()) if hasattr(z["Fs"], "item") else int(z["Fs"])
        else:
            raise KeyError(f"No sample-rate key ('rate'/'Fs') in {stim_path}")

    # Match the stable playback parameters used in GUI_sections.create_pure_tone
    sd.play(signal, samplerate=fs, blocking=True, blocksize=8192)
    sd.stop()
    time.sleep(1)


for stim in ["7-07", "9-17", "10-95", "14-14","scary_noise"]:
    play_npz_stim(stim)
