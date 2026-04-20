from gpiozero import MCP3008
import time
import statistics

phADC = MCP3008(channel=0)
tdsADC = MCP3008(channel=2)

VREF = 5.0
SCOUNT = 30
temperature = 25

tds_buffer = []
last_sample_time = 0
last_calc_time = 0

def read_ph():
    voltage = phADC.value * VREF
    ph = (3.66 - voltage) / 0.168
    return ph, voltage

def get_median(values):
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return sorted_vals[n // 2]
    else:
        return (sorted_vals[n // 2] + sorted_vals[n // 2 - 1]) / 2.0

def read_tds():
    global last_sample_time, last_calc_time, tds_buffer

    current_time = time.time()

    # Sample every 40ms
    if current_time - last_sample_time > 0.04:
        raw_adc = tdsADC.value * 1024.0
        tds_buffer.append(raw_adc)
        if len(tds_buffer) > SCOUNT:
            tds_buffer.pop(0)
        last_sample_time = current_time

    # Calculate every 800ms
    if current_time - last_calc_time > 0.8 and len(tds_buffer) == SCOUNT:
        median_adc = get_median(tds_buffer)
        average_voltage = median_adc * VREF / 1024.0

        # Temperature compensation
        compensation_coeff = 1.0 + 0.02 * (temperature - 25.0)
        compensation_voltage = average_voltage / compensation_coeff

        # Convert voltage to TDS using official polynomial
        tds_value = (133.42 * compensation_voltage**3 - 255.86 * compensation_voltage**2 + 857.39 * compensation_voltage) * 0.5

        last_calc_time = current_time
        return tds_value, average_voltage

    return None, None

print("--- pH & TDS Live Readings ---")
try:
    while True:
        ph, ph_volt = read_ph()
        tds, tds_volt = read_tds()

        if tds is not None:
            print(f"pH: {ph:.2f} | TDS: {tds:.0f}ppm | TDS voltage: {tds_volt:.4f} | pH voltage: {ph_volt:.4f}")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped.")
