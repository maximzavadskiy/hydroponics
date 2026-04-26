from gpiozero import MCP3008, OutputDevice
from gpiozero.mixins import GPIOQueue
import statistics
import time
import subprocess
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from server import app, db, SensorData, Snapshot
from flow_sensor import get_flowrate, flow_sensor
from gpiozero import Motor
from signal import pause

# Define motors (Forward Pin, Backward Pin)
# Motor 1: Controlled speed (0.25-1.0)
motor1 = Motor(forward=17, backward=27)
# Motor 2: Full speed (GPIO 22-23)
motor2 = Motor(forward=22, backward=23)
# Light driver (GPIO 24)
light_driver = OutputDevice(24)

phADC = MCP3008(channel=0 )
tdsADC = MCP3008(channel=1)

VREF = 5.0
temperature = 25

tds_queue = GPIOQueue(tdsADC, queue_len=30, sample_wait=0.04, partial=True, average=statistics.mean)
tds_queue.start()

snapshot_dir = Path(__file__).parent / "snapshots"
snapshot_dir.mkdir(exist_ok=True)
last_snapshot_time = 0
last_db_log_time = 0
motor_speed = 1.0  # Start at full speed
motor_start_time = time.time()
light_on = False

# Light schedule: 9am to 1am (16 hours)
LIGHT_ON_HOUR = 9
LIGHT_OFF_HOUR = 1  # 1am next day

def read_ph():
    voltage = phADC.value * VREF
    ph = (3.66 - voltage) / 0.168
    return ph

def read_tds():
    median_raw = tds_queue.value
    voltage = median_raw / 1024.0 * VREF
    compensation_coeff = 1.0 + 0.02 * (temperature - 25.0)
    compensation_voltage = voltage / compensation_coeff
    tds_value = (133.42 * compensation_voltage**3 - 255.86 * compensation_voltage**2 + 857.39 * compensation_voltage) * 0.5
    return tds_value, voltage

def take_snapshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = snapshot_dir / f"snapshot_{timestamp}.jpg"
    subprocess.run(["rpicam-still", "-o", str(filepath), "-t", "1000"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return filepath

print("--- pH & TDS Live Readings ---")
try:
    with app.app_context():
        while True:
            ph = read_ph()
            tds, tds_volt = read_tds()
            flow_rate, avg_flow, total_liters = get_flowrate()
            print(f"pH: {ph:.2f} | TDS: {tds:.0f}ppm | TDS voltage: {tds_volt:.4f}V | Flow: {flow_rate:.2f}L/min (avg: {avg_flow:.2f}L/min) | Total: {total_liters:.3f}L | Motor: {motor_speed}")

            current_time = time.time()

            # Motor control: full power for 60 seconds, then 0.25 power
            elapsed = current_time - motor_start_time
            if elapsed < 30:
                motor_speed = 1.0
            else:
                motor_speed = 0.7

            motor1.forward(speed=motor_speed)
            motor2.forward(speed=1.0)

            # Light schedule: 9am to 1am (16 hours)
            current_hour = datetime.now().hour
            if LIGHT_ON_HOUR <= current_hour < 24 or current_hour < LIGHT_OFF_HOUR:
                light_driver.on()
                light_on = True
            else:
                light_driver.off()
                light_on = False

            # Log to database every 10 seconds
            if current_time - last_db_log_time >= 10:
                sensor_entry = SensorData(ph=ph, tds=tds, tds_voltage=tds_volt, motor_speed=motor_speed, light_on=light_on)
                db.session.add(sensor_entry)
                db.session.commit()
                last_db_log_time = current_time

            # Take snapshot every 60 seconds
            if current_time - last_snapshot_time >= 60:
                filepath = take_snapshot()
                snapshot = Snapshot(filename=filepath.name)
                db.session.add(snapshot)
                db.session.commit()
                print(f"Snapshot saved: {filepath}")
                last_snapshot_time = current_time

            time.sleep(1)

except KeyboardInterrupt:
    tds_queue.stop()
    print("\nStopped.")
