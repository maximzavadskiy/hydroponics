#!/usr/bin/env python3
import subprocess
import psutil
import time
from pathlib import Path

script_path = Path(__file__).parent / "ph-convert.py"
log_file = Path(__file__).parent / "watchdog.log"

def is_running(process_name="ph-convert.py"):
    """Check if the process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if process_name in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def restart_app():
    """Restart the application"""
    try:
        subprocess.Popen(['python3', str(script_path)])
        log_message(f"App restarted successfully")
    except Exception as e:
        log_message(f"Error restarting app: {e}")

def log_message(msg):
    """Log message to file"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

if __name__ == '__main__':
    if not is_running():
        log_message("ph-convert.py not running - restarting")
        restart_app()
    else:
        log_message("ph-convert.py is running")
