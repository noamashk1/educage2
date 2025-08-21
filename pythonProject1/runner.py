import os
import sys
import time
import psutil
import subprocess
from datetime import datetime


# Configuration
MAX_RSS_MB = 160          # Restart if resident memory exceeds this (MB)
MAX_UPTIME_S = 6 * 3600   # Or if process runs longer than this many seconds
CHECK_INTERVAL_S = 5      # How often to check (seconds)


def format_mb(bytes_val: int) -> str:
    return f"{bytes_val / (1024 * 1024):.1f} MB"


def child_tree_rss_mb(proc: psutil.Process) -> float:
    """Sum RSS of the process and all its children (if any)."""
    try:
        procs = [proc] + proc.children(recursive=True)
        rss = 0
        for p in procs:
            try:
                rss += p.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return rss / (1024 * 1024)
    except psutil.NoSuchProcess:
        return 0.0


def run_once(cmd: list[str]) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd)
    p = psutil.Process(proc.pid)
    start_time = time.time()

    reason = None
    try:
        while True:
            ret = proc.poll()
            if ret is not None:
                reason = f"Process exited with code {ret}"
                break

            rss_mb = child_tree_rss_mb(p)
            uptime = time.time() - start_time

            if rss_mb > MAX_RSS_MB:
                reason = f"Memory threshold exceeded: {rss_mb:.1f} MB > {MAX_RSS_MB} MB"
                break
            if uptime > MAX_UPTIME_S:
                reason = f"Uptime threshold exceeded: {uptime/3600:.2f} h"
                break

            time.sleep(CHECK_INTERVAL_S)
    except KeyboardInterrupt:
        reason = "KeyboardInterrupt"
    finally:
        if proc.poll() is None:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Stopping child ({reason})...")
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Child stopped ({reason}).")


def main() -> None:
    python = sys.executable  # Use current interpreter/venv
    script = os.path.join(os.getcwd(), "experiment.py")
    cmd = [python, script]

    print(f"Supervisor starting. Thresholds: MAX_RSS_MB={MAX_RSS_MB}, MAX_UPTIME_S={MAX_UPTIME_S}s")
    while True:
        run_once(cmd)
        print("Restarting in 3 seconds...")
        time.sleep(3)


if __name__ == "__main__":
    try:
        import psutil  # noqa: F401  (ensures helpful error if missing)
    except ImportError:
        print("psutil not installed. Run: pip install psutil")
        sys.exit(1)
    main()