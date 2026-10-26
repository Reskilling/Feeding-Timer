import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feeding_timer import FeedingLog, format_clock_time, format_countdown, is_feeding_current, next_reset_time


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


class IsFeedingCurrentTest(unittest.TestCase):
    def test_current_until_next_reset(self):
        fed_at = datetime(2026, 10, 26, 7, 0)
        self.assertTrue(is_feeding_current(fed_at, datetime(2026, 10, 26, 16, 29, 59)))
        self.assertFalse(is_feeding_current(fed_at, datetime(2026, 10, 26, 16, 30)))

    def test_evening_feeding_lasts_overnight(self):
        fed_at = datetime(2026, 10, 26, 18, 0)
        self.assertTrue(is_feeding_current(fed_at, datetime(2026, 10, 27, 5, 59)))
        self.assertFalse(is_feeding_current(fed_at, datetime(2026, 10, 27, 6, 0)))

    def test_feeding_in_the_future_is_not_current(self):
        self.assertFalse(is_feeding_current(datetime(2026, 10, 27, 7, 0), datetime(2026, 10, 26, 7, 0)))


class FormatCountdownTest(unittest.TestCase):
    def test_formats_hours_minutes_seconds(self):
        self.assertEqual(format_countdown(timedelta(hours=1, minutes=2, seconds=3)), "1:02:03")

    def test_does_not_wrap_past_a_day(self):
        self.assertEqual(format_countdown(timedelta(hours=25)), "25:00:00")

    def test_zero(self):
        self.assertEqual(format_countdown(timedelta(0)), "0:00:00")


class FormatClockTimeTest(unittest.TestCase):
    def test_drops_leading_zero_from_hour(self):
        self.assertEqual(format_clock_time(datetime(2026, 10, 26, 7, 5)), "7:05 AM")

    def test_afternoon_uses_pm(self):
        self.assertEqual(format_clock_time(datetime(2026, 10, 26, 16, 30)), "4:30 PM")


class FeedingLogTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log = FeedingLog(os.path.join(self.temp_dir.name, "nested", "state.json"))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_remembers_saved_feeding(self):
        fed_at = datetime(2026, 10, 26, 7, 5, 30)
        self.log.save_fed_at(fed_at)
        self.assertEqual(self.log.load_fed_at(), fed_at)

    def test_missing_file_means_no_feeding(self):
        self.assertIsNone(self.log.load_fed_at())

    def test_corrupt_file_means_no_feeding(self):
        os.makedirs(os.path.dirname(self.log.path))
        with open(self.log.path, "w") as file:
            file.write("not json")
        self.assertIsNone(self.log.load_fed_at())

    def test_timezone_aware_record_loads_as_local_time(self):
        os.makedirs(os.path.dirname(self.log.path))
        with open(self.log.path, "w") as file:
            file.write('{"fed_at": "2026-10-26T07:05:00+00:00"}')
        expected = datetime(2026, 10, 26, 7, 5, tzinfo=timezone.utc).astimezone().replace(tzinfo=None)
        self.assertEqual(self.log.load_fed_at(), expected)

    def test_save_leaves_no_temp_file(self):
        self.log.save_fed_at(datetime(2026, 10, 26, 7, 5))
        self.assertEqual(os.listdir(os.path.dirname(self.log.path)), ["state.json"])

    def test_clear_forgets_feeding_and_tolerates_missing_file(self):
        self.log.save_fed_at(datetime(2026, 10, 26, 7, 5))
        self.log.clear()
        self.log.clear()
        self.assertIsNone(self.log.load_fed_at())


if __name__ == "__main__":
    unittest.main()
