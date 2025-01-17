"""Unit tests for storm_events_io.py."""

import unittest
import numpy
from gewittergefahr.gg_io import storm_events_io

YEAR_1DIGIT = 2
YEAR_2DIGITS = 33
YEAR_3DIGITS = 707
YEAR_4DIGITS = 3094
YEAR_5DIGITS = 40550

YEAR_STRING_1DIGIT = '0002'
YEAR_STRING_2DIGITS = '0033'
YEAR_STRING_3DIGITS = '0707'
YEAR_STRING_4DIGITS = '3094'
YEAR_STRING_5DIGITS = '40550'

TIME_ZONE_STRING_WITH_NUMBER = 'CST-6'
TIME_ZONE_STRING_NO_NUMBER = 'CST'
TIME_ZONE_STRING_INVALID = 'foo'
UTC_OFFSET_HOURS = -6

STRING_WITH_1MONTH_NO_CAPS = '06-jun-11 04:20:00'
STRING_WITH_1MONTH_ALL_CAPS = '06-JUN-11 04:20:00'
STRING_WITH_1MONTH_WRONG_CAPS = '06-jUN-11 04:20:00'
STRING_WITH_1MONTH_CORRECT_CAPS = '06-Jun-11 04:20:00'

STRING_WITH_NO_MONTHS = 'foobar'
STRING_WITH_MANY_MONTHS = '30 days are in april, JUNE, september, and NOVEMBER'
STRING_WITH_MANY_MONTHS_FIXED = (
    '30 days are in April, June, September, and November')

TIME_STRING = '15-SEP-17 21:58:33'
TIME_UNIX_SEC = 1505512713

# SLW = straight-line wind.
EVENT_TYPE_STRING_SLW_NO_CAPS = 'thunderstorm wind'
EVENT_TYPE_STRING_SLW_ALL_CAPS = 'THUNDERSTORM WIND'
EVENT_TYPE_STRING_SLW_SOME_CAPS = 'ThUnDeRsToRm WiNd'
EVENT_TYPE_STRING_SLW_TRAILING_WHITESPACE = '\t   thunderstorm wind \r\n'
EVENT_TYPE_STRING_NOT_SLW = 'tornado'

NUM_WIND_REPORTS = 11
FAKE_STATION_IDS = [
    '000000_storm_events', '000001_storm_events', '000002_storm_events',
    '000003_storm_events', '000004_storm_events', '000005_storm_events',
    '000006_storm_events', '000007_storm_events', '000008_storm_events',
    '000009_storm_events', '000010_storm_events']

YEAR_FOR_RAW_FILE = 2015
RAW_DIRECTORY_NAME = 'storm_events/raw_files'
RAW_FILE_NAME = 'storm_events/raw_files/storm_events2015.csv'


class StormEventsIoTests(unittest.TestCase):
    """Each method is a unit test for storm_events_io.py."""

    def test_year_number_to_string_1digit(self):
        """Ensures correctness of _year_number_to_string for 1-digit year."""

        this_year_string = storm_events_io._year_number_to_string(YEAR_1DIGIT)
        self.assertTrue(this_year_string == YEAR_STRING_1DIGIT)

    def test_year_number_to_string_2digits(self):
        """Ensures correctness of _year_number_to_string for 2-digit year."""

        this_year_string = storm_events_io._year_number_to_string(YEAR_2DIGITS)
        self.assertTrue(this_year_string == YEAR_STRING_2DIGITS)

    def test_year_number_to_string_3digits(self):
        """Ensures correctness of _year_number_to_string for 3-digit year."""

        this_year_string = storm_events_io._year_number_to_string(YEAR_3DIGITS)
        self.assertTrue(this_year_string == YEAR_STRING_3DIGITS)

    def test_year_number_to_string_4digits(self):
        """Ensures correctness of _year_number_to_string for 4-digit year."""

        this_year_string = storm_events_io._year_number_to_string(YEAR_4DIGITS)
        self.assertTrue(this_year_string == YEAR_STRING_4DIGITS)

    def test_year_number_to_string_5digits(self):
        """Ensures correctness of _year_number_to_string for 5-digit year."""

        this_year_string = storm_events_io._year_number_to_string(YEAR_5DIGITS)
        self.assertTrue(this_year_string == YEAR_STRING_5DIGITS)

    def test_time_zone_to_utc_offset_string_with_number(self):
        """Ensures correct output from _time_zone_string_to_utc_offset.

        In this case, time-zone string has number at the end.
        """

        this_utc_offset_hours = storm_events_io._time_zone_string_to_utc_offset(
            TIME_ZONE_STRING_WITH_NUMBER)
        self.assertTrue(this_utc_offset_hours == UTC_OFFSET_HOURS)

    def test_time_zone_to_utc_offset_string_no_number(self):
        """Ensures correct output from _time_zone_string_to_utc_offset.

        In this case, time-zone string has no number at the end.
        """

        this_utc_offset_hours = storm_events_io._time_zone_string_to_utc_offset(
            TIME_ZONE_STRING_NO_NUMBER)
        self.assertTrue(this_utc_offset_hours == UTC_OFFSET_HOURS)

    def test_time_zone_to_utc_offset_string_invalid(self):
        """Ensures correct output from _time_zone_string_to_utc_offset.

        In this case, time-zone string is invalid.
        """

        this_utc_offset_hours = storm_events_io._time_zone_string_to_utc_offset(
            TIME_ZONE_STRING_INVALID)
        self.assertTrue(numpy.isnan(this_utc_offset_hours))

    def test_capitalize_months_1month_no_caps(self):
        """Ensures correct output from _capitalize_months.

        In this case, original string contains 1 month with no caps.
        """

        this_new_string = storm_events_io._capitalize_months(
            STRING_WITH_1MONTH_NO_CAPS)
        self.assertTrue(this_new_string == STRING_WITH_1MONTH_CORRECT_CAPS)

    def test_capitalize_months_1month_all_caps(self):
        """Ensures correct output from _capitalize_months.

        In this case, original string contains 1 month in ALL CAPS.
        """

        this_new_string = storm_events_io._capitalize_months(
            STRING_WITH_1MONTH_ALL_CAPS)
        self.assertTrue(this_new_string == STRING_WITH_1MONTH_CORRECT_CAPS)

    def test_capitalize_months_1month_wrong_caps(self):
        """Ensures correct output from _capitalize_months.

        In this case, original string contains 1 month with the wrONG
        CAPitalization.
        """

        this_new_string = storm_events_io._capitalize_months(
            STRING_WITH_1MONTH_WRONG_CAPS)
        self.assertTrue(this_new_string == STRING_WITH_1MONTH_CORRECT_CAPS)

    def test_capitalize_months_1month_correct_caps(self):
        """Ensures correct output from _capitalize_months.

        In this case, original string contains 1 month with the correct caps.
        """

        this_new_string = storm_events_io._capitalize_months(
            STRING_WITH_1MONTH_CORRECT_CAPS)
        self.assertTrue(this_new_string == STRING_WITH_1MONTH_CORRECT_CAPS)

    def test_capitalize_months_no_months(self):
        """Ensures correct output from _capitalize_months.

        In this case, original string contains no months.
        """

        this_new_string = storm_events_io._capitalize_months(
            STRING_WITH_NO_MONTHS)
        self.assertTrue(this_new_string == STRING_WITH_NO_MONTHS)

    def test_capitalize_months_many_months(self):
        """Ensures correct output from _capitalize_months.

        In this case, original string contains many months with the wrONG
        CAPitalization.
        """

        this_new_string = storm_events_io._capitalize_months(
            STRING_WITH_MANY_MONTHS)
        self.assertTrue(this_new_string == STRING_WITH_MANY_MONTHS_FIXED)

    def test_time_string_to_unix_sec(self):
        """Ensures correct output from _time_string_to_unix_sec."""

        this_time_unix_sec = storm_events_io._time_string_to_unix_sec(
            TIME_STRING)
        self.assertTrue(this_time_unix_sec == TIME_UNIX_SEC)

    def test_is_event_thunderstorm_wind_no_caps(self):
        """Ensures correct output from _is_event_thunderstorm_wind.

        In this case, the event-type string has no caps.
        """

        this_flag = storm_events_io._is_event_thunderstorm_wind(
            EVENT_TYPE_STRING_SLW_NO_CAPS)
        self.assertTrue(this_flag)

    def test_is_event_thunderstorm_wind_all_caps(self):
        """Ensures correct output from _is_event_thunderstorm_wind.

        In this case, the event-type string has all caps.
        """

        this_flag = storm_events_io._is_event_thunderstorm_wind(
            EVENT_TYPE_STRING_SLW_ALL_CAPS)
        self.assertTrue(this_flag)

    def test_is_event_thunderstorm_wind_some_caps(self):
        """Ensures correct output from _is_event_thunderstorm_wind.

        In this case, the event-type string has some caps.
        """

        this_flag = storm_events_io._is_event_thunderstorm_wind(
            EVENT_TYPE_STRING_SLW_SOME_CAPS)
        self.assertTrue(this_flag)

    def test_is_event_thunderstorm_wind_trailing_whitespace(self):
        """Ensures correct output from _is_event_thunderstorm_wind.

        In this case, the event-type string has a lot of trailing whitespace.
        """

        this_flag = storm_events_io._is_event_thunderstorm_wind(
            EVENT_TYPE_STRING_SLW_TRAILING_WHITESPACE)
        self.assertTrue(this_flag)

    def test_is_event_thunderstorm_wind_tornado(self):
        """Ensures correct output from _is_event_thunderstorm_wind.

        In this case, the event type is tornado.
        """

        this_flag = storm_events_io._is_event_thunderstorm_wind(
            EVENT_TYPE_STRING_NOT_SLW)
        self.assertFalse(this_flag)

    def test_generate_fake_station_ids(self):
        """Ensures correct output from _generate_fake_station_ids."""

        these_station_ids = storm_events_io._generate_fake_station_ids(
            NUM_WIND_REPORTS)
        self.assertTrue(these_station_ids == FAKE_STATION_IDS)

    def test_find_local_raw_file(self):
        """Ensures correct output from find_local_raw_file."""

        this_file_name = storm_events_io.find_local_raw_file(
            YEAR_FOR_RAW_FILE, directory_name=RAW_DIRECTORY_NAME,
            raise_error_if_missing=False)
        self.assertTrue(this_file_name == RAW_FILE_NAME)


if __name__ == '__main__':
    unittest.main()
