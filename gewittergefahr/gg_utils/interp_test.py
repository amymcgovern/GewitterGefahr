"""Unit tests for interp.py."""

import copy
import unittest
import numpy
from gewittergefahr.gg_utils import interp

TOLERANCE = 1e-6

# The following constants are used to test _find_nearest_value.
SORTED_ARRAY = numpy.array([-5., -3., -1., 0., 1.5, 4., 9.])
TEST_VALUES = numpy.array([-6., -5., -4., -3., 5., 8., 9., 10.])
NEAREST_INDICES_FOR_TEST_VALUES = numpy.array([0., 0., 1., 1., 5., 6., 6., 6.])

# The following constants are used to test _stack_1d_arrays_horizontally.
LIST_OF_1D_ARRAYS = [numpy.array([1., 2., 3]),
                     numpy.array([0., 5., 10.]),
                     numpy.array([6., 6., 6.])]
MATRIX_FIRST_ARRAY = numpy.reshape(LIST_OF_1D_ARRAYS[0], (3, 1))
MATRIX_FIRST_2ARRAYS = numpy.transpose(
    numpy.array([[1., 2., 3.], [0., 5., 10.]]))
MATRIX_FIRST_3ARRAYS = numpy.transpose(
    numpy.array([[1., 2., 3.], [0., 5., 10.], [6., 6., 6.]]))

# The following constants are used to test _find_heights_with_temperature.
TARGET_TEMPERATURE_KELVINS = 10.
WARM_TEMPERATURES_KELVINS = numpy.array(
    [10., 10., 10., 11., 11., 11., 12., 12., 12., numpy.nan, numpy.nan, 12.])
COLD_TEMPERATURES_KELVINS = numpy.array(
    [8., 9., 10., 8., 9., 10., 8., 9., 10., numpy.nan, 8., numpy.nan])
WARM_HEIGHTS_M_ASL = numpy.full(9, 2000.)
COLD_HEIGHTS_M_ASL = numpy.full(9, 2500.)

TARGET_HEIGHTS_M_ASL = numpy.array(
    [2000., 2000., numpy.nan, 2166.666667, 2250., 2500., 2250., 2333.333333,
     2500., numpy.nan, numpy.nan, numpy.nan])

# The following constants are used to test interp_in_time.
INPUT_MATRIX_TIME0 = numpy.array([[0., 2., 5., 10.],
                                  [-2., 1., 3., 6.],
                                  [-3.5, -2.5, 3., 8.]])
INPUT_MATRIX_TIME4 = numpy.array([[2., 5., 7., 15.],
                                  [0., 2., 5., 8.],
                                  [-1.5, -2.5, 0., 4.]])

INPUT_TIMES_UNIX_SEC = numpy.array([0, 4])
LINEAR_INTERP_TIMES_UNIX_SEC = numpy.array([1, 2, 3])
LINEAR_EXTRAP_TIMES_UNIX_SEC = numpy.array([8])
INPUT_MATRIX_FOR_TEMPORAL_INTERP = numpy.stack(
    (INPUT_MATRIX_TIME0, INPUT_MATRIX_TIME4), axis=-1)

THIS_QUERY_MATRIX_TIME1 = numpy.array([[0.5, 2.75, 5.5, 11.25],
                                       [-1.5, 1.25, 3.5, 6.5],
                                       [-3., -2.5, 2.25, 7.]])
THIS_QUERY_MATRIX_TIME2 = numpy.array([[1., 3.5, 6., 12.5],
                                       [-1., 1.5, 4., 7.],
                                       [-2.5, -2.5, 1.5, 6.]])
THIS_QUERY_MATRIX_TIME3 = numpy.array([[1.5, 4.25, 6.5, 13.75],
                                       [-0.5, 1.75, 4.5, 7.5],
                                       [-2., -2.5, 0.75, 5.]])
THIS_QUERY_MATRIX_TIME8 = numpy.array([[4., 8., 9., 20.],
                                       [2., 3., 7., 10.],
                                       [0.5, -2.5, -3., 0.]])

EXPECTED_MATRIX_FOR_LINEAR_INTERP = numpy.stack(
    (THIS_QUERY_MATRIX_TIME1, THIS_QUERY_MATRIX_TIME2,
     THIS_QUERY_MATRIX_TIME3), axis=-1)
EXPECTED_MATRIX_FOR_LINEAR_EXTRAP = numpy.expand_dims(
    THIS_QUERY_MATRIX_TIME8, axis=-1)

PREV_INTERP_TIMES_UNIX_SEC = numpy.array([1, 2, 3, 8])
THIS_QUERY_MATRIX_TIME1 = copy.deepcopy(INPUT_MATRIX_TIME0)
THIS_QUERY_MATRIX_TIME2 = copy.deepcopy(INPUT_MATRIX_TIME0)
THIS_QUERY_MATRIX_TIME3 = copy.deepcopy(INPUT_MATRIX_TIME0)
THIS_QUERY_MATRIX_TIME8 = copy.deepcopy(INPUT_MATRIX_TIME4)
EXPECTED_MATRIX_FOR_PREV_INTERP = numpy.stack(
    (THIS_QUERY_MATRIX_TIME1, THIS_QUERY_MATRIX_TIME2,
     THIS_QUERY_MATRIX_TIME3, THIS_QUERY_MATRIX_TIME8), axis=-1)

NEXT_INTERP_TIMES_UNIX_SEC = numpy.array([1, 2, 3])
THIS_QUERY_MATRIX_TIME1 = copy.deepcopy(INPUT_MATRIX_TIME4)
THIS_QUERY_MATRIX_TIME2 = copy.deepcopy(INPUT_MATRIX_TIME4)
THIS_QUERY_MATRIX_TIME3 = copy.deepcopy(INPUT_MATRIX_TIME4)
EXPECTED_MATRIX_FOR_NEXT_INTERP = numpy.stack(
    (THIS_QUERY_MATRIX_TIME1, THIS_QUERY_MATRIX_TIME2,
     THIS_QUERY_MATRIX_TIME3), axis=-1)

# The following constants are used to test interp_from_xy_grid_to_points.
INPUT_MATRIX_FOR_SPATIAL_INTERP = numpy.array([[17., 24., 1., 8.],
                                               [23., 5., 7., 14.],
                                               [4., 6., 13., 20.],
                                               [10., 12., 19., 21.],
                                               [11., 18., 25., 2.]])

SPLINE_DEGREE = 1  # linear
GRID_POINT_X_METRES = numpy.array([0., 1., 2., 3.])
GRID_POINT_Y_METRES = numpy.array([0., 2., 4., 6., 8.])
QUERY_X_FOR_SPLINE_INTERP_METRES = numpy.array([0., 0.5, 1., 1.5, 2., 2.5, 3.])
QUERY_Y_FOR_SPLINE_INTERP_METRES = numpy.array([0., 2., 2.5, 3., 5., 6., 7.5])
QUERY_VALUES_FOR_SPLINE_INTERP = numpy.array(
    [17., 14., 5.25, 7.75, 16., 20., 6.75])

QUERY_X_FOR_NEAREST_NEIGH_METRES = numpy.array(
    [0., 0.3, 0.7, 1.2, 1.8, 2.1, 2.9])
QUERY_Y_FOR_NEAREST_NEIGH_METRES = numpy.array(
    [0.5, 1.5, 2.5, 4., 5.5, 6.5, 7.7])
EXPECTED_QUERY_VALUES_FOR_NEAREST_NEIGH = numpy.array(
    [17., 23., 5., 6., 19., 19., 2])

QUERY_X_FOR_EXTRAP_METRES = numpy.array([-1., 4.])
QUERY_Y_FOR_EXTRAP_METRES = numpy.array([-2., 10.])
QUERY_VALUES_FOR_EXTRAP = numpy.array([17., 2.])


class InterpTests(unittest.TestCase):
    """Each method is a unit test for interp.py."""

    def test_find_nearest_value(self):
        """Ensures correct output from _find_nearest_value."""

        these_nearest_indices = numpy.full(len(TEST_VALUES), -1)
        for i in range(len(TEST_VALUES)):
            _, these_nearest_indices[i] = interp._find_nearest_value(
                SORTED_ARRAY, TEST_VALUES[i])

        self.assertTrue(numpy.array_equal(
            these_nearest_indices, NEAREST_INDICES_FOR_TEST_VALUES))

    def test_stack_1d_arrays_horizontally_1array(self):
        """Ensures correct output from _stack_1d_arrays_horizontally.

        In this case there is one input array.
        """

        these_indices = numpy.array([0], dtype=int)
        this_matrix = interp._stack_1d_arrays_horizontally(
            [LIST_OF_1D_ARRAYS[i] for i in these_indices])

        self.assertTrue(numpy.allclose(
            this_matrix, MATRIX_FIRST_ARRAY, atol=TOLERANCE))

    def test_stack_1d_arrays_horizontally_2arrays(self):
        """Ensures correct output from _stack_1d_arrays_horizontally.

        In this case there are 2 input arrays.
        """

        these_indices = numpy.array([0, 1], dtype=int)
        this_matrix = interp._stack_1d_arrays_horizontally(
            [LIST_OF_1D_ARRAYS[i] for i in these_indices])

        self.assertTrue(numpy.allclose(
            this_matrix, MATRIX_FIRST_2ARRAYS, atol=TOLERANCE))

    def test_stack_1d_arrays_horizontally_3arrays(self):
        """Ensures correct output from _stack_1d_arrays_horizontally.

        In this case there are 3 input arrays.
        """

        these_indices = numpy.array([0, 1, 2], dtype=int)
        this_matrix = interp._stack_1d_arrays_horizontally(
            [LIST_OF_1D_ARRAYS[i] for i in these_indices])

        self.assertTrue(numpy.allclose(
            this_matrix, MATRIX_FIRST_3ARRAYS, atol=TOLERANCE))

    def test_find_heights_with_temperature(self):
        """Ensures correct output from _find_heights_with_temperature."""

        these_heights_m_asl = interp._find_heights_with_temperature(
            warm_temperatures_kelvins=WARM_TEMPERATURES_KELVINS,
            cold_temperatures_kelvins=COLD_TEMPERATURES_KELVINS,
            warm_heights_m_asl=WARM_HEIGHTS_M_ASL,
            cold_heights_m_asl=COLD_HEIGHTS_M_ASL,
            target_temperature_kelvins=TARGET_TEMPERATURE_KELVINS)

        self.assertTrue(numpy.allclose(
            these_heights_m_asl, TARGET_HEIGHTS_M_ASL, atol=TOLERANCE,
            equal_nan=True))

    def test_check_temporal_interp_method_good(self):
        """Ensures correct output from check_temporal_interp_method.

        In this case, input is a valid temporal-interp method.
        """

        interp.check_temporal_interp_method(interp.NEAREST_INTERP_METHOD)

    def test_check_temporal_interp_method_bad(self):
        """Ensures correct output from check_temporal_interp_method.

        In this case, input is *not* a valid temporal method.
        """

        with self.assertRaises(ValueError):
            interp.check_temporal_interp_method(interp.SPLINE_INTERP_METHOD)

    def test_check_spatial_interp_method_good(self):
        """Ensures correct output from check_spatial_interp_method.

        In this case, input is a valid spatial-interp method.
        """

        interp.check_spatial_interp_method(interp.SPLINE_INTERP_METHOD)

    def test_check_spatial_interp_method_bad(self):
        """Ensures correct output from check_spatial_interp_method.

        In this case, input is *not* a valid spatial method.
        """

        with self.assertRaises(ValueError):
            interp.check_spatial_interp_method(interp.PREVIOUS_INTERP_METHOD)

    def test_interp_in_time_linear_no_extrap(self):
        """Ensures correct output from interp_in_time.

        In this case, method is linear with no extrapolation.
        """

        this_query_matrix = interp.interp_in_time(
            INPUT_MATRIX_FOR_TEMPORAL_INTERP,
            sorted_input_times_unix_sec=INPUT_TIMES_UNIX_SEC,
            query_times_unix_sec=LINEAR_INTERP_TIMES_UNIX_SEC,
            method_string=interp.LINEAR_INTERP_METHOD)

        self.assertTrue(numpy.allclose(
            this_query_matrix, EXPECTED_MATRIX_FOR_LINEAR_INTERP,
            atol=TOLERANCE))

    def test_interp_in_time_linear_extrap(self):
        """Ensures correct output from interp_in_time.

        In this case, method is linear with extrapolation.
        """

        this_query_matrix = interp.interp_in_time(
            INPUT_MATRIX_FOR_TEMPORAL_INTERP,
            sorted_input_times_unix_sec=INPUT_TIMES_UNIX_SEC,
            query_times_unix_sec=LINEAR_EXTRAP_TIMES_UNIX_SEC,
            method_string=interp.LINEAR_INTERP_METHOD, allow_extrap=True)
        self.assertTrue(numpy.allclose(
            this_query_matrix, EXPECTED_MATRIX_FOR_LINEAR_EXTRAP,
            atol=TOLERANCE))

    def test_interp_in_time_previous(self):
        """Ensures correct output from interp_in_time.

        In this case, method is previous-neighbour.
        """

        this_query_matrix = interp.interp_in_time(
            INPUT_MATRIX_FOR_TEMPORAL_INTERP,
            sorted_input_times_unix_sec=INPUT_TIMES_UNIX_SEC,
            query_times_unix_sec=PREV_INTERP_TIMES_UNIX_SEC,
            method_string=interp.PREVIOUS_INTERP_METHOD)
        self.assertTrue(numpy.allclose(
            this_query_matrix, EXPECTED_MATRIX_FOR_PREV_INTERP, atol=TOLERANCE))

    def test_interp_in_time_next(self):
        """Ensures correct output from interp_in_time.

        In this case, method is next-neighbour.
        """

        this_query_matrix = interp.interp_in_time(
            INPUT_MATRIX_FOR_TEMPORAL_INTERP,
            sorted_input_times_unix_sec=INPUT_TIMES_UNIX_SEC,
            query_times_unix_sec=NEXT_INTERP_TIMES_UNIX_SEC,
            method_string=interp.NEXT_INTERP_METHOD)
        self.assertTrue(numpy.allclose(
            this_query_matrix, EXPECTED_MATRIX_FOR_NEXT_INTERP, atol=TOLERANCE))

    def test_interp_from_xy_grid_to_points_spline_interp(self):
        """Ensures correct output from interp_from_xy_grid_to_points.

        In this case, doing interpolation with linear spline.
        """

        these_query_values = interp.interp_from_xy_grid_to_points(
            INPUT_MATRIX_FOR_SPATIAL_INTERP,
            sorted_grid_point_x_metres=GRID_POINT_X_METRES,
            sorted_grid_point_y_metres=GRID_POINT_Y_METRES,
            query_x_metres=QUERY_X_FOR_SPLINE_INTERP_METRES,
            query_y_metres=QUERY_Y_FOR_SPLINE_INTERP_METRES,
            method_string=interp.SPLINE_INTERP_METHOD,
            spline_degree=SPLINE_DEGREE)

        self.assertTrue(numpy.allclose(
            these_query_values, QUERY_VALUES_FOR_SPLINE_INTERP,
            atol=TOLERANCE))

    def test_interp_from_xy_grid_to_points_spline_extrap(self):
        """Ensures correct output from interp_from_xy_grid_to_points.

        In this case, doing extrapolation with linear spline.
        """

        these_query_values = interp.interp_from_xy_grid_to_points(
            INPUT_MATRIX_FOR_SPATIAL_INTERP,
            sorted_grid_point_x_metres=GRID_POINT_X_METRES,
            sorted_grid_point_y_metres=GRID_POINT_Y_METRES,
            query_x_metres=QUERY_X_FOR_EXTRAP_METRES,
            query_y_metres=QUERY_Y_FOR_EXTRAP_METRES,
            method_string=interp.SPLINE_INTERP_METHOD,
            spline_degree=SPLINE_DEGREE, allow_extrap=True)

        self.assertTrue(numpy.allclose(
            these_query_values, QUERY_VALUES_FOR_EXTRAP, atol=TOLERANCE))

    def test_interp_from_xy_grid_to_points_nearest(self):
        """Ensures correct output from interp_from_xy_grid_to_points.

        In this case, doing interpolation with nearest-neighbour method.
        """

        these_query_values = interp.interp_from_xy_grid_to_points(
            INPUT_MATRIX_FOR_SPATIAL_INTERP,
            sorted_grid_point_x_metres=GRID_POINT_X_METRES,
            sorted_grid_point_y_metres=GRID_POINT_Y_METRES,
            query_x_metres=QUERY_X_FOR_NEAREST_NEIGH_METRES,
            query_y_metres=QUERY_Y_FOR_NEAREST_NEIGH_METRES,
            method_string=interp.NEAREST_INTERP_METHOD)

        self.assertTrue(numpy.allclose(
            these_query_values, EXPECTED_QUERY_VALUES_FOR_NEAREST_NEIGH,
            atol=TOLERANCE))

    def test_interp_from_xy_grid_to_points_nn_extrap(self):
        """Ensures correct output from interp_from_xy_grid_to_points.

        In this case, doing extrapolation with nearest-neighbour method.
        """

        these_query_values = interp.interp_from_xy_grid_to_points(
            INPUT_MATRIX_FOR_SPATIAL_INTERP,
            sorted_grid_point_x_metres=GRID_POINT_X_METRES,
            sorted_grid_point_y_metres=GRID_POINT_Y_METRES,
            query_x_metres=QUERY_X_FOR_EXTRAP_METRES,
            query_y_metres=QUERY_Y_FOR_EXTRAP_METRES,
            method_string=interp.NEAREST_INTERP_METHOD, allow_extrap=True)

        self.assertTrue(numpy.allclose(
            these_query_values, QUERY_VALUES_FOR_EXTRAP, atol=TOLERANCE))


if __name__ == '__main__':
    unittest.main()
