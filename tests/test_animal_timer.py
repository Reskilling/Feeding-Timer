import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AnimalTimer import format_countdown, next_reset_time


class NextResetTimeTest(unittest.TestCase):
    def assert_next_reset(self, now, expected):
        self.assertEqual(next_reset_time(now), expected)

    def test_before_morning_resets_at_morning_same_day(self):
        self.assert_next_reset(datetime(2026, 10, 26, 0, 0), datetime(2026, 10, 26, 6, 0))
        self.assert_next_reset(datetime(2026, 10, 26, 5, 59, 59), datetime(2026, 10, 26, 6, 0))

    def test_between_morning_and_evening_resets_at_evening(self):
        self.assert_next_reset(datetime(2026, 10, 26, 6, 0), datetime(2026, 10, 26, 16, 30))
        self.assert_next_reset(datetime(2026, 10, 26, 16, 29, 59), datetime(2026, 10, 26, 16, 30))

    def test_after_evening_resets_at_next_morning(self):
        self.assert_next_reset(datetime(2026, 10, 26, 16, 30), datetime(2026, 10, 27, 6, 0))
        self.assert_next_reset(datetime(2026, 12, 31, 23, 59), datetime(2027, 1, 1, 6, 0))


class FormatCountdownTest(unittest.TestCase):
    def test_formats_hours_minutes_seconds(self):
        self.assertEqual(format_countdown(timedelta(hours=1, minutes=2, seconds=3)), "01:02:03")

    def test_does_not_wrap_past_a_day(self):
        self.assertEqual(format_countdown(timedelta(hours=25)), "25:00:00")

    def test_zero(self):
        self.assertEqual(format_countdown(timedelta(0)), "00:00:00")


if __name__ == "__main__":
    unittest.main()
