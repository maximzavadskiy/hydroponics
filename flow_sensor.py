from gpiozero import DigitalInputDevice
import time

# GPIO 26 water flow sensor (YF-S201 or similar)
# Calibration: 7.5 Hz per L/min, 450 pulses per Liter
# Actual calibration factor: 0.909 (adjusted from test: 600mL in 30s = 1.2L/min)
CALIBRATION = 0.909
flow_sensor = DigitalInputDevice(26, pull_up=False)

pulse_count = 0
total_pulses = 0
flow_history = []
start_time = time.time()

def count_pulse():
    global pulse_count, total_pulses
    pulse_count += 1
    total_pulses += 1

flow_sensor.when_activated = count_pulse

def get_flowrate():
    """Return current flowrate, avg flowrate, and total liters"""
    global pulse_count, total_pulses, flow_history

    current_count = pulse_count
    pulse_count = 0

    flow_rate = current_count * 0.00225   # L/min
    total_liters = ((total_pulses / 450) * 2) * CALIBRATION

    # Track flow for averaging (keep last 60 readings = ~1 minute)
    flow_history.append(flow_rate)
    if len(flow_history) > 60:
        flow_history.pop(0)

    avg_flow = sum(flow_history) / len(flow_history) if flow_history else 0

    return flow_rate, avg_flow, total_liters
