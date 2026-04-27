#!/usr/bin/env python3
"""Test lights schedule by enabling test mode and setting off time"""
import sys
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    print("Usage: python3 test_lights_schedule.py <minutes_until_off>")
    print("Example: python3 test_lights_schedule.py 1  # Lights turn off in 1 minute")
    sys.exit(1)

minutes = int(sys.argv[1])
now = datetime.now()
off_time = now + timedelta(minutes=minutes)

print(f"Current time: {now.strftime('%H:%M:%S')}")
print(f"Light ON time: {now.strftime('%H:%M')}")
print(f"Light OFF time: {off_time.strftime('%H:%M')}")
print()
print("To enable this test, update ph-convert.py:")
print(f"  TEST_MODE = True")
print(f"  LIGHT_ON_MINUTE = ({now.hour}, {now.minute})")
print(f"  LIGHT_OFF_MINUTE = ({off_time.hour}, {off_time.minute})")
print()
print("Then restart the hydroponics service:")
print("  sudo systemctl restart hydroponics.service")
print()
print("Observe the lights in the dashboard - they should turn OFF at the scheduled time.")
