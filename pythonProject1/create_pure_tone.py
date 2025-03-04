import numpy as np
from scipy.io.wavfile import write
# import pygame
import numpy as np
import sounddevice as sd

def generate_white_noise(duration, Fs, voltage, filename):
    """
    Generate white noise.

    Parameters:
    duration - Duration of the noise in seconds
    sample_rate - Sample rate in Hz
    
    Returns:
    noise - A NumPy array containing the white noise samples
    """
    # Calculate the number of samples
    num_samples = int(duration * Fs)
    
    # Generate random samples between -1 and 1
    noise = np.random.uniform(-1, 1, num_samples)
    
    # Scale the noise by the voltage (amplitude) before converting to integers
    noise *= voltage  # Adjust the volume

    # Clamp the noise values to ensure they stay within the valid range
    noise = np.clip(noise, -1, 1)
    
    # Convert to 16-bit signed integers
    noise_int16 = np.int16(noise * 32767)
    
        # Write the tone to a WAV file
    write(filename, Fs, noise_int16)
    
    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load your sound file
    sound = pygame.mixer.Sound(filename)  # Use a .wav file

    # Play the sound
    sound.play()

    # To keep the program running while the sound plays
    while pygame.mixer.get_busy():
        pygame.time.delay(100)

    return 
def create_pure_tone(freq, voltage, tone_dur, ramp_dur, Fs):
    """
    Creates and plays a vector of a ramped sine wave with the input parameters.

    Parameters:
    freq       - frequency in kHz
    voltage    - amplitude of wave before attenuation in volts
    tone_dur   - duration of tone in seconds
    ramp_dur   - duration of ramp in seconds
    Fs         - sample rate in Hz

    Returns:
    tone_shape - A numpy array containing the generated tone
    """

    # Create ramp
    ramp_length = int(tone_dur * Fs)
    ramp = np.ones(ramp_length)

    ramp_duration_samples = int(ramp_dur * Fs)

    ramp[:ramp_duration_samples] = np.linspace(0, 1, ramp_duration_samples)
    ramp[-ramp_duration_samples:] = np.linspace(1, 0, ramp_duration_samples)

    # Create time vector
    t = np.arange(tone_dur * Fs)  # time vector from 0 to tone_dur (in samples)

    # Create tone
    tone_shape = voltage * ramp * np.sin(2 * np.pi * freq * 1000 * t / Fs)

    # Play sound
    sd.play(tone_shape, Fs)
    sd.wait()  # Wait until sound finishes playing

    return tone_shape


# Example Usage
freq = 14  # Frequency in kHz (e.g., 440 Hz)
voltage = 1  # Amplitude in volts
tone_dur = 0.5  # Duration in seconds
ramp_dur = 0.05  # Ramp duration in seconds
Fs = 300000  # Sampling rate in Hz
filename = 'pure_tone_4k.wav'  # Name of the output WAV file

tone = create_pure_tone(freq, voltage, tone_dur, ramp_dur, Fs)

duration = 1
noise_filename ="white_noise.wav"
# generate_white_noise(duration, Fs, voltage, noise_filename)



