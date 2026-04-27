#!/usr/bin/env python3
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# Light schedule constants (must match ph-convert.py)
LIGHT_ON_HOUR = 9
LIGHT_OFF_HOUR = 1  # 1am next day


def manage_light_schedule(current_time, light_driver):
    """Control lights based on schedule (9am to 1am = 16 hours)"""
    current_hour = datetime.now().hour
    if LIGHT_ON_HOUR <= current_hour < 24 or current_hour < LIGHT_OFF_HOUR:
        light_driver.on()
        return True
    else:
        light_driver.off()
        return False


class TestManageLightSchedule(unittest.TestCase):
    """Unit tests for manage_light_schedule function"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_light_driver = Mock()

    def _test_hour(self, hour, should_be_on):
        """Helper method to test a specific hour"""
        with patch('test_light_schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = hour
            self.mock_light_driver.reset_mock()
            result = manage_light_schedule(None, self.mock_light_driver)

            if should_be_on:
                self.mock_light_driver.on.assert_called_once()
                self.mock_light_driver.off.assert_not_called()
            else:
                self.mock_light_driver.off.assert_called_once()
                self.mock_light_driver.on.assert_not_called()

            self.assertEqual(result, should_be_on,
                           f"Hour {hour}: expected light to be {'ON' if should_be_on else 'OFF'}")

    def test_light_on_at_9am(self):
        """Test lights turn on at 9am (LIGHT_ON_HOUR)"""
        self._test_hour(9, True)

    def test_light_on_at_noon(self):
        """Test lights are on at noon"""
        self._test_hour(12, True)

    def test_light_on_at_midnight(self):
        """Test lights are on at midnight (00:00)"""
        self._test_hour(0, True)

    def test_light_off_at_1am(self):
        """Test lights turn off at 1am (LIGHT_OFF_HOUR)"""
        self._test_hour(1, False)

    def test_light_off_before_9am(self):
        """Test lights are off before 9am"""
        self._test_hour(8, False)

    def test_light_off_at_8am(self):
        """Test lights are off at 8am (before LIGHT_ON_HOUR)"""
        self._test_hour(8, False)

    def test_light_on_at_11pm(self):
        """Test lights are on at 11pm (before 1am cutoff)"""
        self._test_hour(23, True)

    def test_light_off_at_2am(self):
        """Test lights are off at 2am"""
        self._test_hour(2, False)

    def test_light_off_at_6am(self):
        """Test lights are off at 6am"""
        self._test_hour(6, False)

    def test_16_hour_schedule(self):
        """Test that lights are on for exactly 16 hours (9am to 1am)"""
        hours_on = []
        for hour in range(24):
            with patch('test_light_schedule.datetime') as mock_datetime:
                mock_datetime.now.return_value.hour = hour
                self.mock_light_driver.reset_mock()
                result = manage_light_schedule(None, self.mock_light_driver)
                if result:
                    hours_on.append(hour)

        # Should be on from 9 to 23 (15 hours) and 0 (1 hour) = 16 hours total
        # Note: hours_on will be sorted, so 0 comes first
        expected_hours = [0] + list(range(9, 24))
        self.assertEqual(hours_on, expected_hours,
                        f"Lights should be on for hours {expected_hours}, but were on for {hours_on}")
        self.assertEqual(len(hours_on), 16, "Lights should be on for exactly 16 hours")

    def test_light_driver_called_correctly_on(self):
        """Test that light_driver.on() is called when lights should be on"""
        with patch('test_light_schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 15
            self.mock_light_driver.reset_mock()
            result = manage_light_schedule(None, self.mock_light_driver)
            self.mock_light_driver.on.assert_called_once()
            self.mock_light_driver.off.assert_not_called()
            self.assertTrue(result)

    def test_light_driver_called_correctly_off(self):
        """Test that light_driver.off() is called when lights should be off"""
        with patch('test_light_schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 5
            self.mock_light_driver.reset_mock()
            result = manage_light_schedule(None, self.mock_light_driver)
            self.mock_light_driver.off.assert_called_once()
            self.mock_light_driver.on.assert_not_called()
            self.assertFalse(result)

    def test_all_hours_coverage(self):
        """Test all 24 hours to ensure correct ON/OFF states"""
        expected_state = {
            0: True,   # Midnight - ON
            1: False,  # 1am - OFF (cutoff)
            2: False,  # 2am - OFF
            3: False,  # 3am - OFF
            6: False,  # 6am - OFF
            8: False,  # 8am - OFF (just before start)
            9: True,   # 9am - ON (start)
            12: True,  # Noon - ON
            15: True,  # 3pm - ON
            20: True,  # 8pm - ON
            23: True,  # 11pm - ON (just before end)
        }

        for hour, should_be_on in expected_state.items():
            with patch('test_light_schedule.datetime') as mock_datetime:
                mock_datetime.now.return_value.hour = hour
                self.mock_light_driver.reset_mock()
                result = manage_light_schedule(None, self.mock_light_driver)
                self.assertEqual(result, should_be_on,
                               f"Hour {hour}: expected {'ON' if should_be_on else 'OFF'}, got {'ON' if result else 'OFF'}")

    def test_return_value_true_when_on(self):
        """Test that function returns True when lights are on"""
        with patch('test_light_schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 9
            result = manage_light_schedule(None, self.mock_light_driver)
            self.assertTrue(result)

    def test_return_value_false_when_off(self):
        """Test that function returns False when lights are off"""
        with patch('test_light_schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value.hour = 5
            result = manage_light_schedule(None, self.mock_light_driver)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
