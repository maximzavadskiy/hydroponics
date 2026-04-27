#!/usr/bin/env python3
import subprocess
import psutil
import time
import requests
from pathlib import Path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log_file = Path(__file__).parent / "watchdog.log"

def is_running(process_name):
    """Check if the process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if process_name in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def restart_service(service_name):
    """Restart a systemd service"""
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)
        log_message(f"{service_name} restarted successfully")
    except Exception as e:
        log_message(f"Error restarting {service_name}: {e}")

def restart_localtunnel():
    """Restart localtunnel systemd service"""
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'localtunnel.service'], check=True)
        log_message("localtunnel restarted successfully")
    except Exception as e:
        log_message(f"Error restarting localtunnel: {e}")

def check_server_health():
    """Check if server is responding"""
    try:
        response = requests.get('http://localhost:5000/api/app-status', timeout=2)
        return response.status_code == 200
    except:
        return False

def check_tunnel_health():
    """Check if tunnel is responding to public requests"""
    try:
        response = requests.get('https://hydroponics-max.loca.lt/api/app-status', timeout=5, verify=False)
        return response.status_code == 200
    except:
        return False

def log_message(msg):
    """Log message to file"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")

if __name__ == '__main__':
    # Check sensor app
    if not is_running("ph-convert.py"):
        log_message("ph-convert.py not running - restarting via systemd")
        restart_service("hydroponics.service")

    # Check server health
    if not check_server_health():
        log_message("Server not responding - restarting via systemd")
        restart_service("hydroponics-server.service")

    # Check localtunnel - test actual tunnel health, not just process
    tunnel_ok = is_running("localtunnel") and check_tunnel_health()
    if not tunnel_ok:
        log_message("localtunnel not responding - restarting")
        restart_localtunnel()
        time.sleep(3)  # Give tunnel time to establish connection
    else:
        log_message("All services healthy")
