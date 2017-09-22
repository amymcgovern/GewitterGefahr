"""IO methods for reports of damaging SLW* in the Storm Events database.

* SLW = straight-line wind
"""

import numpy
import pandas
import time
import calendar
from gewittergefahr.gg_io import myrorss_io
from gewittergefahr.gg_io import raw_wind_io

# TODO(thunderhoser): add error-checking to all methods.
# TODO(thunderhoser): replace main method with named high-level method.

ORIG_CSV_FILE_NAME = (
    '/localdata/ryan.lagerquist/software/matlab/madis/raw_files/storm_events/'
    'storm_events2011.csv')

NEW_CSV_FILE_NAME = '/localdata/ryan.lagerquist/aasswp/slw_reports_2011.csv'

HOURS_TO_SECONDS = 3600
KT_TO_METRES_PER_SECOND = 1.852 / 3.6

TIME_COLUMN_ORIG = 'BEGIN_DATE_TIME'
EVENT_TYPE_COLUMN_ORIG = 'EVENT_TYPE'
TIME_ZONE_COLUMN_ORIG = 'CZ_TIMEZONE'
WIND_SPEED_COLUMN_ORIG = 'MAGNITUDE'
LATITUDE_COLUMN_ORIG = 'BEGIN_LAT'
LONGITUDE_COLUMN_ORIG = 'BEGIN_LON'

REQUIRED_EVENT_TYPE = 'thunderstorm wind'

TIME_ZONE_STRINGS = ['PST', 'PST-8', 'MST', 'MST-7', 'CST', 'CST-6', 'EST',
                     'EST-5', 'AST', 'AST-4']
UTC_OFFSETS_HOURS = numpy.array([-8, -8, -7, -7, -6, -6, -5, -5, -4, -4])

MONTH_NAMES_3LETTERS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                        'Sep', 'Oct', 'Nov', 'Dec']
TIME_FORMAT = '%d-%b-%y %H:%M:%S'


def _time_zone_string_to_utc_offset(time_zone_string):
    """Converts time zone from string to UTC offset.

    :param time_zone_string: String describing time zone (examples: "PST",
        "MST", etc.).
    :return: utc_offset_hours: Difference between local time and UTC (local
        minus UTC).
    """

    time_zone_string = time_zone_string.strip().upper()
    tz_string_flags = [s == time_zone_string for s in TIME_ZONE_STRINGS]
    if not any(tz_string_flags):
        return numpy.nan

    tz_string_index = numpy.where(tz_string_flags)[0][0]
    return UTC_OFFSETS_HOURS[tz_string_index]


def _capitalize_months(orig_string):
    """Converts string to all lower-case, except first letter of each month.

    :param orig_string: Original string.
    :return: new_string: New string.
    """

    new_string = orig_string.lower()
    for i in range(len(MONTH_NAMES_3LETTERS)):
        new_string = new_string.replace(MONTH_NAMES_3LETTERS[i].lower(),
                                        MONTH_NAMES_3LETTERS[i])

    return new_string


def _time_string_to_unix_sec(time_string):
    """Converts time from string to Unix format (sec since 0000 UTC 1 Jan 1970).

    :param time_string: Time string (format "dd-mmm-yy HH:MM:SS").
    :return: unix_time_sec: Time in Unix format.
    """

    time_string = _capitalize_months(time_string)
    return calendar.timegm(time.strptime(time_string, TIME_FORMAT))


def _local_time_string_to_unix_sec(local_time_string, utc_offset_hours):
    """Converts time from local string to Unix format.

    Unix format = seconds since 0000 UTC 1 Jan 1970.

    :param local_time_string: Local time, formatted as "dd-mmm-yy HH:MM:SS".
    :param utc_offset_hours: Difference between UTC and local time zone (local
        minus UTC).
    :return: unix_time_sec: Seconds since 0000 UTC 1 Jan 1970.
    """

    local_time_unix_sec = _time_string_to_unix_sec(local_time_string)
    return local_time_unix_sec - utc_offset_hours * HOURS_TO_SECONDS


def _is_event_thunderstorm_wind(event_type_string):
    """Determines whether or not event type is thunderstorm wind.

    :param event_type_string: String description of event.  Must contain
        "thunderstorm wind," with any combination of capital and lower-case
        letters.
    :return: is_thunderstorm_wind: Boolean flag, either True or False.
    """

    index_of_thunderstorm_wind = event_type_string.lower().find(
        REQUIRED_EVENT_TYPE)
    return index_of_thunderstorm_wind != -1


def _remove_invalid_data(wind_table):
    """Removes any row with invalid data.

    "Invalid data" means that either [a] time is NaN or [b] latitude, longitude,
    or wind speed is out of range.

    :param wind_table: pandas DataFrame created by
        read_slw_reports_from_orig_csv.
    :return: wind_table: Same as input, except that any row with invalid data
        has been removed.
    """

    invalid_flags = numpy.isnan(wind_table[raw_wind_io.TIME_COLUMN].values)
    invalid_indices = numpy.where(invalid_flags)[0]
    wind_table.drop(wind_table.index[invalid_indices], axis=0, inplace=True)

    invalid_indices = raw_wind_io.check_latitudes(
        wind_table[raw_wind_io.LATITUDE_COLUMN].values)
    wind_table.drop(wind_table.index[invalid_indices], axis=0, inplace=True)

    invalid_indices = raw_wind_io.check_longitudes(
        wind_table[raw_wind_io.LONGITUDE_COLUMN].values)
    wind_table.drop(wind_table.index[invalid_indices], axis=0, inplace=True)

    absolute_v_winds_m_s01 = numpy.absolute(
        wind_table[raw_wind_io.V_WIND_COLUMN].values)
    invalid_indices = raw_wind_io.check_wind_speeds(absolute_v_winds_m_s01)
    wind_table.drop(wind_table.index[invalid_indices], axis=0, inplace=True)

    wind_table[
        raw_wind_io.LONGITUDE_COLUMN] = myrorss_io.convert_lng_positive_in_west(
        wind_table[raw_wind_io.LONGITUDE_COLUMN].values)
    return wind_table


def read_slw_reports_from_orig_csv(csv_file_name):
    """Reads SLW reports from original CSV file (one in the raw database).

    :param csv_file_name: Path to input file.
    :return: wind_table: pandas DataFrame with the following columns.
    wind_table.latitude_deg: Latitude (deg N).
    wind_table.longitude_deg: Longitude (deg E).
    wind_table.unix_time_sec: Observation time (seconds since 0000 UTC 1 Jan
        1970).
    wind_table.u_wind_m_s01: u-component of wind (m/s), assuming that all
        directions are due north.
    wind_table.v_wind_m_s01: v-component of wind (m/s), assuming that all
        directions are due north.
    """

    report_table = pandas.read_csv(csv_file_name, header=0, sep=',')

    num_reports = len(report_table.index)
    thunderstorm_wind_flags = numpy.full(num_reports, False, dtype=bool)
    for i in range(num_reports):
        thunderstorm_wind_flags[i] = _is_event_thunderstorm_wind(
            report_table[EVENT_TYPE_COLUMN_ORIG].values[i])

    non_tstorm_wind_indices = (
        numpy.where(numpy.invert(thunderstorm_wind_flags))[0])
    report_table.drop(report_table.index[non_tstorm_wind_indices], axis=0,
                      inplace=True)

    num_reports = len(report_table.index)
    unix_times_sec = numpy.full(num_reports, numpy.nan, dtype=int)
    for i in range(num_reports):
        this_utc_offset_hours = _time_zone_string_to_utc_offset(
            report_table[TIME_ZONE_COLUMN_ORIG].values[i])
        if numpy.isnan(this_utc_offset_hours):
            continue

        unix_times_sec[i] = _local_time_string_to_unix_sec(
            report_table[TIME_COLUMN_ORIG].values[i], this_utc_offset_hours)

    # Wind direction is not included in storm reports, so assume due north.
    u_winds_m_s01 = numpy.full(num_reports, 0.)
    v_winds_m_s01 = -KT_TO_METRES_PER_SECOND * report_table[
        WIND_SPEED_COLUMN_ORIG].values

    wind_dict = {raw_wind_io.TIME_COLUMN: unix_times_sec,
                 raw_wind_io.LATITUDE_COLUMN: report_table[
                     LATITUDE_COLUMN_ORIG].values,
                 raw_wind_io.LONGITUDE_COLUMN: report_table[
                     LONGITUDE_COLUMN_ORIG].values,
                 raw_wind_io.U_WIND_COLUMN: u_winds_m_s01,
                 raw_wind_io.V_WIND_COLUMN: v_winds_m_s01}

    wind_table = pandas.DataFrame.from_dict(wind_dict)
    return _remove_invalid_data(wind_table)


if __name__ == '__main__':
    wind_table = read_slw_reports_from_orig_csv(ORIG_CSV_FILE_NAME)
    print wind_table

    raw_wind_io.write_winds_to_csv(wind_table, NEW_CSV_FILE_NAME)