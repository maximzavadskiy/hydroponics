from gpiozero import MCP3008
from gpiozero.mixins import GPIOQueue
import statistics
import time

phADC = MCP3008(channel=0)
tdsADC = MCP3008(channel=2)

VREF = 5.0
temperature = 25

tds_queue = GPIOQueue(tdsADC, queue_len=30, sample_wait=0.04, partial=False, average=statistics.median)
tds_queue.start()

def read_ph():
    voltage = phADC.value * VREF
    ph = (3.66 - voltage) / 0.168
    return ph, voltage

def read_tds():
    median_raw = tds_queue.value
    voltage = median_raw / 1024.0 * VREF
    compensation_coeff = 1.0 + 0.02 * (temperature - 25.0)
    compensation_voltage = voltage / compensation_coeff
    tds_value = (133.42 * compensation_voltage**3 - 255.86 * compensation_voltage**2 + 857.39 * compensation_voltage) * 0.5
    return tds_value, voltage

print("--- pH & TDS Live Readings ---")
try:
    while True:
        ph, ph_volt = read_ph()
        tds, tds_volt = read_tds()
        print(f"pH: {ph:.2f} | TDS: {tds:.0f}ppm | TDS voltage: {tds_volt:.4f} | pH voltage: {ph_volt:.4f}")
        time.sleep(1)

except KeyboardInterrupt:
    tds_queue.stop()
    print("\nStopped.")
