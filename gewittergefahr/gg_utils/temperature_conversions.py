"""Conversion methods for temperature."""

from gewittergefahr.gg_utils import error_checking

FAHRENHEIT_TO_CELSIUS_ADDEND = -32.
FAHRENHEIT_TO_CELSIUS_RATIO = 5. / 9.
CELSIUS_TO_KELVINS_ADDEND = 273.15


def fahrenheit_to_celsius(temperatures_deg_f):
    """Converts temperatures from Fahrenheit (deg F) to Celsius (deg C).

    :param temperatures_deg_f: numpy array of temperatures in deg F.
    :return: temperatures_deg_c: equivalent-size numpy array of temperatures in
        deg C.
    """

    error_checking.assert_is_real_numpy_array(temperatures_deg_f)
    return ((temperatures_deg_f +
             FAHRENHEIT_TO_CELSIUS_ADDEND) * FAHRENHEIT_TO_CELSIUS_RATIO)


def celsius_to_kelvins(temperatures_deg_c):
    """Converts temperatures from Celsius (deg C) to Kelvins.

    :param temperatures_deg_c: numpy array of temperatures in deg C.
    :return: temperatures_kelvins: equivalent-size numpy array of temperatures
        in Kelvins.
    """

    error_checking.assert_is_real_numpy_array(temperatures_deg_c)
    return temperatures_deg_c + CELSIUS_TO_KELVINS_ADDEND


def kelvins_to_celsius(temperatures_kelvins):
    """Converts temperatures from Kelvins to Celsius (deg C).

    :param temperatures_kelvins: numpy array of temperatures in Kelvins.
    :return: temperatures_deg_c: equivalent-size numpy array of temperatures in
        deg C.
    """

    error_checking.assert_is_real_numpy_array(temperatures_kelvins)
    return temperatures_kelvins - CELSIUS_TO_KELVINS_ADDEND


def celsius_to_fahrenheit(temperatures_deg_c):
    """Converts temperatures from Celsius (deg C) to Fahrenheit (deg F).

    :param temperatures_deg_c: numpy array of temperatures in deg C.
    :return: temperatures_deg_f: equivalent-size numpy array of temperatures in
        deg F.
    """

    error_checking.assert_is_real_numpy_array(temperatures_deg_c)
    return (temperatures_deg_c /
            FAHRENHEIT_TO_CELSIUS_RATIO) - FAHRENHEIT_TO_CELSIUS_ADDEND


def fahrenheit_to_kelvins(temperatures_deg_f):
    """Converts temperatures from Fahrenheit (deg F) to Kelvins.

    :param temperatures_deg_f: numpy array of temperatures in deg F.
    :return: temperatures_kelvins: equivalent-size numpy array of temperatures
        in Kelvins.
    """

    return celsius_to_kelvins(fahrenheit_to_celsius(temperatures_deg_f))


def kelvins_to_fahrenheit(temperatures_kelvins):
    """Converts temperatures from Kelvins to Fahrenheit (deg F).

    :param temperatures_kelvins: numpy array of temperatures in Kelvins.
    :return: temperatures_deg_f: equivalent-size numpy array of temperatures in
        deg F.
    """

    return celsius_to_fahrenheit(kelvins_to_celsius(temperatures_kelvins))
