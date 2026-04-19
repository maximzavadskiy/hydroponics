from gpiozero import MCP3008
import time

phADC = MCP3008(channel=0)
tdsADC = MCP3008(channel=2)

VREF = 5      # match your MCP3008 supply voltage (3.3 or 5.0)
TDS_FACTOR = 400  # voltage to PPM conversion (adjust based on sensor calibration)

def read_ph():
    voltage = phADC.value * VREF
    ph = (3.66 - voltage) / 0.168
    return ph, voltage

def read_tds():
    voltage = tdsADC.value * VREF
    ppm = voltage * TDS_FACTOR
    return ppm, voltage

print("--- pH & TDS Live Readings ---")
try:
    while True:
        ph, ph_volt = read_ph()
        tds, tds_volt = read_tds()
        print(f"pH: {ph:.2f} | TDS: {tds:.0f}ppm")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped.")
