import tkinter as tk
from tkinter import filedialog, messagebox
import importlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram, butter, sosfiltfilt


def normalize_audio(x: np.ndarray) -> np.ndarray:
    """Convert audio to float32 in [-1, 1] when possible."""
    if x.dtype.kind in ("i", "u"):
        max_val = np.iinfo(x.dtype).max
        if max_val == 0:
            return x.astype(np.float32)
        return x.astype(np.float32) / max_val
    return x.astype(np.float32)


def moving_rms(signal: np.ndarray, win_samples: int, hop_samples: int):
    """Compute frame-wise RMS with overlap control."""
    if win_samples <= 0 or hop_samples <= 0:
        raise ValueError("Window and hop must be positive.")
    if len(signal) < win_samples:
        return np.array([]), np.array([])

    frames = []
    times = []
    for start in range(0, len(signal) - win_samples + 1, hop_samples):
        frame = signal[start:start + win_samples]
        rms = float(np.sqrt(np.mean(frame ** 2)))
        frames.append(rms)
        times.append(start + win_samples / 2)
    return np.array(frames), np.array(times)


def detect_segments(times_sec: np.ndarray, values: np.ndarray, threshold: float):
    """Return contiguous (start, end) segments where values >= threshold."""
    if len(values) == 0:
        return []
    mask = values >= threshold
    segments = []
    start_idx = None
    for i, flag in enumerate(mask):
        if flag and start_idx is None:
            start_idx = i
        elif not flag and start_idx is not None:
            segments.append((times_sec[start_idx], times_sec[i - 1]))
            start_idx = None
    if start_idx is not None:
        segments.append((times_sec[start_idx], times_sec[-1]))
    return segments


def dominant_frequency_for_segment(
    f_hz: np.ndarray,
    t_sec: np.ndarray,
    spec_mag: np.ndarray,
    start_sec: float,
    end_sec: float
):
    """
    Return dominant frequency (Hz) for a time segment from spectrogram magnitude.
    Dominance is measured by mean magnitude across all time bins in segment.
    """
    if len(f_hz) == 0 or len(t_sec) == 0 or spec_mag.size == 0:
        return None
    time_mask = (t_sec >= start_sec) & (t_sec <= end_sec)
    if not np.any(time_mask):
        return None

    segment_slice = spec_mag[:, time_mask]
    if segment_slice.size == 0:
        return None

    mean_mag_per_freq = segment_slice.mean(axis=1)
    if mean_mag_per_freq.size == 0:
        return None
    dominant_idx = int(np.argmax(mean_mag_per_freq))
    return float(f_hz[dominant_idx])


class WavAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WAV RMS + 5-20kHz Spectrogram")
        self.wav_path = tk.StringVar()

        tk.Label(root, text="WAV file:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        tk.Entry(root, textvariable=self.wav_path, width=55).grid(row=0, column=1, padx=8, pady=6)
        tk.Button(root, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=8, pady=6)

        tk.Label(root, text="RMS threshold (0-1):").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.rms_thresh_entry = tk.Entry(root, width=10)
        self.rms_thresh_entry.insert(0, "0.08")
        self.rms_thresh_entry.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        tk.Label(root, text="RMS window (ms):").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.rms_win_entry = tk.Entry(root, width=10)
        self.rms_win_entry.insert(0, "40")
        self.rms_win_entry.grid(row=2, column=1, sticky="w", padx=8, pady=6)

        tk.Label(root, text="RMS hop (ms):").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        self.rms_hop_entry = tk.Entry(root, width=10)
        self.rms_hop_entry.insert(0, "10")
        self.rms_hop_entry.grid(row=3, column=1, sticky="w", padx=8, pady=6)

        tk.Label(root, text="Spectrogram window (ms):").grid(row=4, column=0, sticky="w", padx=8, pady=6)
        self.spec_win_entry = tk.Entry(root, width=10)
        self.spec_win_entry.insert(0, "80")
        self.spec_win_entry.grid(row=4, column=1, sticky="w", padx=8, pady=6)

        self.show_events_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            root,
            text="Show high-RMS detections on spectrogram",
            variable=self.show_events_var
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=8, pady=6)

        tk.Button(root, text="Analyze", command=self.analyze).grid(row=6, column=0, columnspan=3, pady=12)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[
                ("Audio files", "*.wav *.flac *.aiff *.aif *.ogg"),
                ("WAV files", "*.wav"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.wav_path.set(path)

    def load_audio(self, path: str):
        """
        Load audio file.
        - Standard WAV (RIFF/RIFX/RF64): scipy.wavfile
        - Other formats: fallback to soundfile (if installed)
        """
        with open(path, "rb") as f:
            header = f.read(4)
        if header in (b"RIFF", b"RIFX", b"RF64"):
            return wavfile.read(path)

        # Fallback for non-WAV containers/codecs
        try:
            sf = importlib.import_module("soundfile")
        except Exception:
            raise ValueError(
                "This file is not a standard WAV (RIFF/RIFX/RF64).\n"
                "Install soundfile to read additional formats:\n"
                "pip install soundfile\n"
                "Or convert/export the file to PCM WAV and try again."
            )

        audio, fs = sf.read(path, always_2d=False)
        return int(fs), audio

    def analyze(self):
        try:
            wav_path = self.wav_path.get().strip()
            if not wav_path:
                raise ValueError("Please select a WAV file.")

            rms_threshold = float(self.rms_thresh_entry.get())
            rms_win_ms = float(self.rms_win_entry.get())
            rms_hop_ms = float(self.rms_hop_entry.get())
            spec_win_ms = float(self.spec_win_entry.get())

            fs, audio = self.load_audio(wav_path)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)  # Convert stereo to mono
            audio = normalize_audio(audio)

            # Band-pass 5-20kHz for analysis relevance
            nyq = fs / 2
            low = 5000 / nyq
            high = 20000 / nyq
            if high >= 1:
                raise ValueError("Sampling rate too low for 20kHz analysis.")
            sos = butter(4, [low, high], btype="band", output="sos")
            band_audio = sosfiltfilt(sos, audio)

            rms_win = max(1, int(fs * rms_win_ms / 1000))
            rms_hop = max(1, int(fs * rms_hop_ms / 1000))
            rms_vals, rms_times_samples = moving_rms(band_audio, rms_win, rms_hop)
            rms_times_sec = rms_times_samples / fs if len(rms_times_samples) else np.array([])
            segments = detect_segments(rms_times_sec, rms_vals, rms_threshold)

            nperseg = max(16, int(fs * spec_win_ms / 1000))
            noverlap = int(0.75 * nperseg)
            f, t, sxx = spectrogram(
                band_audio,
                fs=fs,
                window="hann",
                nperseg=nperseg,
                noverlap=noverlap,
                detrend=False,
                scaling="density",
                mode="magnitude",
            )

            band_mask = (f >= 5000) & (f <= 20000)
            f_band = f[band_mask]
            sxx_band = sxx[band_mask, :]
            sxx_db = 20 * np.log10(sxx_band + 1e-10)

            fig, ax = plt.subplots(figsize=(11, 6))
            pcm = ax.pcolormesh(t, f_band / 1000.0, sxx_db, shading="gouraud", cmap="magma")
            plt.colorbar(pcm, ax=ax, label="Magnitude (dB)")
            ax.set_title("Spectrogram (5-20 kHz)")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Frequency (kHz)")

            if self.show_events_var.get():
                for idx, (start, end) in enumerate(segments, start=1):
                    ax.axvspan(start, end, color="cyan", alpha=0.22)
                    dom_freq_hz = dominant_frequency_for_segment(f_band, t, sxx_band, start, end)
                    if dom_freq_hz is None:
                        continue

                    event_center_t = (start + end) / 2.0
                    dom_freq_khz = dom_freq_hz / 1000.0
                    ax.plot(event_center_t, dom_freq_khz, marker="o", markersize=4, color="cyan")
                    ax.text(
                        event_center_t,
                        dom_freq_khz + 0.25,
                        f"E{idx}: {dom_freq_khz:.4f} kHz",
                        color="cyan",
                        fontsize=8,
                        ha="center",
                        va="bottom",
                        bbox={"facecolor": "black", "alpha": 0.35, "pad": 2},
                    )

            txt = (
                f"RMS threshold={rms_threshold:.3f} | "
                f"RMS win={rms_win_ms:.1f}ms, hop={rms_hop_ms:.1f}ms | "
                f"Events={len(segments)}"
            )
            ax.text(
                0.01, 0.98, txt, transform=ax.transAxes,
                va="top", ha="left",
                bbox={"facecolor": "black", "alpha": 0.45, "pad": 5},
                color="white", fontsize=9
            )
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = WavAnalyzerApp(root)
    root.mainloop()
