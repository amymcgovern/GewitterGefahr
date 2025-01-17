"""Methods for handling map projections.

Specifically, this file contains methods for initializing a projection,
converting from lat-long to projection (x-y) coordinates, and converting from
x-y back to lat-long.
"""

import numpy
from pyproj import Proj
from gewittergefahr.gg_utils import error_checking
from gewittergefahr.gg_utils import longitude_conversion as lng_conversion

EARTH_RADIUS_METRES = 6370997.


def init_lambert_conformal_projection(standard_latitudes_deg,
                                      central_longitude_deg):
    """Initializes Lambert conformal projection.

    :param standard_latitudes_deg: length-2 numpy array with standard parallels
        (deg N).  standard_latitudes_deg[0] is the first standard parallel;
        standard_latitudes_deg[1] is the second standard parallel.
    :param central_longitude_deg: central meridian (deg E).
    :return: projection_object: object created by `pyproj.Proj`, specifying the
        Lambert conformal projection.
    """

    error_checking.assert_is_valid_lat_numpy_array(standard_latitudes_deg)
    error_checking.assert_is_numpy_array(standard_latitudes_deg,
                                         exact_dimensions=numpy.array([2]))

    error_checking.assert_is_non_array(central_longitude_deg)
    central_longitude_deg = lng_conversion.convert_lng_positive_in_west(
        central_longitude_deg, allow_nan=False)

    return Proj(proj='lcc', lat_1=standard_latitudes_deg[0],
                lat_2=standard_latitudes_deg[1], lon_0=central_longitude_deg,
                rsphere=EARTH_RADIUS_METRES, ellps='sphere')


def init_azimuthal_equidistant_projection(central_latitude_deg,
                                          central_longitude_deg):
    """Initializes azimuthal equidistant projection.

    :param central_latitude_deg: Central latitude (deg N).
    :param central_longitude_deg: Central longitude (deg E).
    :return: projection_object: object created by `pyproj.Proj`, specifying the
        Lambert conformal projection.
    """

    error_checking.assert_is_valid_latitude(central_latitude_deg)
    error_checking.assert_is_non_array(central_longitude_deg)
    central_longitude_deg = lng_conversion.convert_lng_positive_in_west(
        central_longitude_deg, allow_nan=False)

    return Proj(proj='aeqd', lat_0=central_latitude_deg,
                lon_0=central_longitude_deg)


def init_cylindrical_equal_area_projection(min_latitude_deg=None,
                                           max_latitude_deg=None,
                                           min_longitude_deg=None,
                                           max_longitude_deg=None):
    """Initializes cylindrical equal-area projection.

    :param min_latitude_deg: Latitude at bottom-left corner (deg N).
    :param max_latitude_deg: Latitude at top-right corner (deg N).
    :param min_longitude_deg: Longitude at bottom-left corner (deg E).
    :param max_longitude_deg: Longitude at top-right corner (deg E).
    :return: projection_object: object created by `pyproj.Proj`, specifying the
        cylindrical equal-area projection.
    """

    error_checking.assert_is_valid_latitude(min_latitude_deg)
    error_checking.assert_is_valid_latitude(max_latitude_deg)
    error_checking.assert_is_greater(max_latitude_deg, min_latitude_deg)

    min_longitude_deg = lng_conversion.convert_lng_positive_in_west(
        min_longitude_deg, allow_nan=False)
    max_longitude_deg = lng_conversion.convert_lng_positive_in_west(
        max_longitude_deg, allow_nan=False)
    error_checking.assert_is_greater(max_longitude_deg, min_longitude_deg)

    return Proj(
        proj='cea', llcrnrlat=min_latitude_deg, urcrnrlat=max_latitude_deg,
        llcrnrlon=min_longitude_deg, urcrnrlon=max_longitude_deg)


def init_lambert_azimuthal_equal_area_projection(standard_latitude_deg=None,
                                                 central_latitude_deg=None,
                                                 central_longitude_deg=None):
    """Initializes Lambert azimuthal equal-area projection.

    :param standard_latitude_deg: Standard latitude (latitude of true scale)
        (deg N).
    :param central_latitude_deg: Central latitude (deg N).
    :param central_longitude_deg: Central longitude (deg E).
    :return: projection_object: object created by `pyproj.Proj`, specifying the
        Lambert azimuthal equal-area projection.
    """

    error_checking.assert_is_valid_latitude(standard_latitude_deg)
    error_checking.assert_is_valid_latitude(central_latitude_deg)
    central_longitude_deg = lng_conversion.convert_lng_positive_in_west(
        central_longitude_deg, allow_nan=False)

    return Proj(
        proj='laea', lat_ts=standard_latitude_deg, lat_0=central_latitude_deg,
        lon_0=central_longitude_deg)


def project_latlng_to_xy(latitudes_deg, longitudes_deg, projection_object=None,
                         false_easting_metres=0., false_northing_metres=0.):
    """Converts from lat-long to projection (x-y) coordinates.

    S = shape of coordinate arrays.

    :param latitudes_deg: numpy array of latitudes (deg N) with shape S.
    :param longitudes_deg: numpy array of longitudes (deg E) with shape S.
    :param projection_object: Projection object created by `pyproj.Proj`.
    :param false_easting_metres: False easting.  Will be added to all x-
        coordinates.
    :param false_northing_metres: False northing.  Will be added to all y-
        coordinates.
    :return: x_coords_metres: numpy array of x-coordinates with shape S.
    :return: y_coords_metres: numpy array of y-coordinates with shape S.
    """

    error_checking.assert_is_valid_lat_numpy_array(latitudes_deg,
                                                   allow_nan=True)

    shape_of_coord_arrays = latitudes_deg.shape
    error_checking.assert_is_numpy_array(
        longitudes_deg, exact_dimensions=numpy.asarray(shape_of_coord_arrays))
    longitudes_deg = lng_conversion.convert_lng_positive_in_west(longitudes_deg,
                                                                 allow_nan=True)

    error_checking.assert_is_not_nan(false_easting_metres)
    error_checking.assert_is_not_nan(false_northing_metres)

    x_coords_metres, y_coords_metres = projection_object(longitudes_deg,
                                                         latitudes_deg)

    num_points = latitudes_deg.size
    nan_flags = numpy.logical_or(
        numpy.isnan(numpy.reshape(latitudes_deg, num_points)),
        numpy.isnan(numpy.reshape(longitudes_deg, num_points)))
    nan_indices = numpy.where(nan_flags)[0]

    x_coords_metres_flat = numpy.reshape(x_coords_metres, num_points)
    x_coords_metres_flat[nan_indices] = numpy.nan
    x_coords_metres = numpy.reshape(
        x_coords_metres_flat, shape_of_coord_arrays) + false_easting_metres

    y_coords_metres_flat = numpy.reshape(y_coords_metres, num_points)
    y_coords_metres_flat[nan_indices] = numpy.nan
    y_coords_metres = numpy.reshape(
        y_coords_metres_flat, shape_of_coord_arrays) + false_northing_metres

    return x_coords_metres, y_coords_metres


def project_xy_to_latlng(x_coords_metres, y_coords_metres,
                         projection_object=None, false_easting_metres=0.,
                         false_northing_metres=0.):
    """Converts from projection (x-y) to lat-long coordinates.

    P = number of points

    :param x_coords_metres: length-P numpy array of x-coordinates.
    :param y_coords_metres: length-P numpy array of y-coordinates.
    :param projection_object: Projection object created by `pyproj.Proj`.
    :param false_easting_metres: False easting.  Will be subtracted from all x-
        coordinates before conversion.
    :param false_northing_metres: False northing.  Will be subtracted from all
        y-coordinates before conversion.
    :return: latitudes_deg: length-P numpy array of latitudes (deg N).
    :return: longitudes_deg: length-P numpy array of longitudes (deg E).
    """

    error_checking.assert_is_real_numpy_array(x_coords_metres)

    shape_of_coord_arrays = x_coords_metres.shape
    error_checking.assert_is_numpy_array(
        y_coords_metres, exact_dimensions=numpy.asarray(shape_of_coord_arrays))
    error_checking.assert_is_real_numpy_array(y_coords_metres)

    error_checking.assert_is_not_nan(false_easting_metres)
    error_checking.assert_is_not_nan(false_northing_metres)

    (longitudes_deg, latitudes_deg) = projection_object(
        x_coords_metres - false_easting_metres,
        y_coords_metres - false_northing_metres, inverse=True)

    num_points = x_coords_metres.size
    nan_flags = numpy.logical_or(
        numpy.isnan(numpy.reshape(x_coords_metres, num_points)),
        numpy.isnan(numpy.reshape(y_coords_metres, num_points)))
    nan_indices = numpy.where(nan_flags)[0]

    latitudes_deg_flat = numpy.reshape(latitudes_deg, num_points)
    latitudes_deg_flat[nan_indices] = numpy.nan

    longitudes_deg_flat = numpy.reshape(longitudes_deg, num_points)
    longitudes_deg_flat[nan_indices] = numpy.nan
    longitudes_deg_flat = lng_conversion.convert_lng_positive_in_west(
        longitudes_deg_flat, allow_nan=True)

    return (numpy.reshape(latitudes_deg_flat, shape_of_coord_arrays),
            numpy.reshape(longitudes_deg_flat, shape_of_coord_arrays))
