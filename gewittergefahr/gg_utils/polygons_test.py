"""Unit tests for polygons.py."""

import numpy
import unittest
import shapely.geometry
from gewittergefahr.gg_utils import polygons

TOLERANCE = 1e-6

SHORT_LIST = []
MEDIUM_LIST = [0, 1, 2, 3]
LONG_LIST = [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]
LIST_OF_LISTS = [SHORT_LIST, MEDIUM_LIST, LONG_LIST]

EXTERIOR_VERTEX_X_METRES = numpy.array([0., 0., 10., 10., 0.])
EXTERIOR_VERTEX_Y_METRES = numpy.array([0., 10., 10., 0., 0.])
EXTERIOR_VERTEX_METRES_LIST = [(0., 0.), (0., 10.), (10., 10.), (10., 0.),
                               (0., 0.)]

HOLE1_VERTEX_X_METRES = numpy.array([2., 2., 4., 4., 2.])
HOLE1_VERTEX_Y_METRES = numpy.array([2., 4., 4., 2., 2.])
HOLE1_VERTEX_METRES_LIST = [(2., 2.), (2., 4.), (4., 4.), (4., 2.), (2., 2.)]

HOLE2_VERTEX_X_METRES = numpy.array([6., 6., 8., 8., 6.])
HOLE2_VERTEX_Y_METRES = numpy.array([6., 8., 8., 6., 6.])
HOLE2_VERTEX_METRES_LIST = [(6., 6.), (6., 8.), (8., 8.), (8., 6.), (6., 6.)]
NUM_HOLES = 2

MERGED_VERTEX_X_METRES = numpy.array([0., 0., 10., 10., 0., numpy.nan,
                                      2., 2., 4., 4., 2., numpy.nan,
                                      6., 6., 8., 8., 6.])
MERGED_VERTEX_Y_METRES = numpy.array([0., 10., 10., 0., 0., numpy.nan,
                                      2., 4., 4., 2., 2., numpy.nan,
                                      6., 8., 8., 6., 6.])
MERGED_VERTEX_METRES_LIST = [(0., 0.), (0., 10.), (10., 10.), (10., 0.),
                             (0., 0.), (numpy.nan, numpy.nan), (2., 2.),
                             (2., 4.), (4., 4.), (4., 2.), (2., 2.),
                             (numpy.nan, numpy.nan), (6., 6.), (6., 8.),
                             (8., 8.), (8., 6.), (6., 6.)]

POLYGON_OBJECT = shapely.geometry.Polygon(shell=EXTERIOR_VERTEX_METRES_LIST,
                                          holes=(HOLE1_VERTEX_METRES_LIST,
                                                 HOLE2_VERTEX_METRES_LIST))

SMALL_BUFFER_DIST_METRES = 2.5
LARGE_BUFFER_DIST_METRES = 5.

VERTEX_X_METRES_SMALL_BUFFER = numpy.array([-2.5, -2.5, 12.5, 12.5, -2.5])
VERTEX_Y_METRES_SMALL_BUFFER = numpy.array([-2.5, 12.5, 12.5, -2.5, -2.5])

VERTEX_X_METRES_LARGE_BUFFER = numpy.array([-5., -5., 15., 15., -5.])
VERTEX_Y_METRES_LARGE_BUFFER = numpy.array([-5., 15., 15., -5., -5.])

VERTEX_X_METRES_NESTED_BUFFER = numpy.array(
    [-5., -5., 15., 15., -5., numpy.nan, -2.5, -2.5, 12.5, 12.5, -2.5])
VERTEX_Y_METRES_NESTED_BUFFER = numpy.array(
    [-5., 15., 15., -5., -5., numpy.nan, -2.5, 12.5, 12.5, -2.5, -2.5])

FIRST_VERTEX_ROW = 5
FIRST_VERTEX_COLUMN = 5
SECOND_VERTEX_ROW_UP = 4
SECOND_VERTEX_COLUMN_UP = 5
SECOND_VERTEX_ROW_DOWN = 6
SECOND_VERTEX_COLUMN_DOWN = 5
SECOND_VERTEX_ROW_RIGHT = 5
SECOND_VERTEX_COLUMN_RIGHT = 6
SECOND_VERTEX_ROW_LEFT = 5
SECOND_VERTEX_COLUMN_LEFT = 4
SECOND_VERTEX_ROW_UP_RIGHT = 4
SECOND_VERTEX_COLUMN_UP_RIGHT = 6
SECOND_VERTEX_ROW_UP_LEFT = 4
SECOND_VERTEX_COLUMN_UP_LEFT = 4
SECOND_VERTEX_ROW_DOWN_RIGHT = 6
SECOND_VERTEX_COLUMN_DOWN_RIGHT = 6
SECOND_VERTEX_ROW_DOWN_LEFT = 6
SECOND_VERTEX_COLUMN_DOWN_LEFT = 4

ROW_INDICES_IN_POLYGON = numpy.array(
    [101, 101, 102, 102, 102, 102, 103, 103, 103, 104])
COLUMN_INDICES_IN_POLYGON = numpy.array(
    [501, 502, 501, 502, 503, 504, 502, 503, 504, 504])

POINT_IN_POLYGON_MATRIX = numpy.array([[0, 0, 0, 0, 0, 0],
                                       [0, 1, 1, 0, 0, 0],
                                       [0, 1, 1, 1, 1, 0],
                                       [0, 0, 1, 1, 1, 0],
                                       [0, 0, 0, 0, 1, 0],
                                       [0, 0, 0, 0, 0, 0]]).astype(bool)
FIRST_ROW_INDEX = 100
FIRST_COLUMN_INDEX = 500

VERTEX_ROWS_GRID_POINTS = numpy.array(
    [101, 102, 103, 103, 104, 102, 102, 101, 101])
VERTEX_COLUMNS_GRID_POINTS = numpy.array(
    [501, 501, 502, 503, 504, 504, 503, 502, 501])

VERTEX_ROWS_GRID_CELL_EDGES_REDUNDANT = numpy.array(
    [100.5, 102.5, 102.5, 103.5, 103.5, 103.5, 103.5, 103.5, 104.5, 104.5,
     102.5, 103.5, 104.5, 101.5, 101.5, 100.5, 100.5])
VERTEX_COLUMNS_GRID_CELL_EDGES_REDUNDANT = numpy.array(
    [500.5, 500.5, 501.5, 501.5, 503.5, 502.5, 501.5, 503.5, 503.5, 504.5,
     504.5, 504.5, 504.5, 504.5, 502.5, 502.5, 500.5])
VERTEX_ROWS_GRID_CELL_EDGES_NON_REDUNDANT = numpy.array(
    [100.5, 102.5, 102.5, 103.5, 103.5, 104.5, 104.5, 101.5, 101.5, 100.5,
     100.5])
VERTEX_COLUMNS_GRID_CELL_EDGES_NON_REDUNDANT = numpy.array(
    [500.5, 500.5, 501.5, 501.5, 503.5, 503.5, 504.5, 504.5, 502.5, 502.5,
     500.5])


class PolygonsTests(unittest.TestCase):
    """Each method is a unit test for polygons.py."""

    def test_get_longest_inner_list(self):
        """Ensures correct output from _get_longest_inner_list."""

        this_longest_list = polygons._get_longest_inner_list(LIST_OF_LISTS)
        self.assertTrue(this_longest_list == LONG_LIST)

    def test_separate_exterior_and_holes(self):
        """Ensures correct output from _separate_exterior_and_holes."""

        this_vertex_dict = polygons._separate_exterior_and_holes(
            MERGED_VERTEX_X_METRES, MERGED_VERTEX_Y_METRES)

        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.EXTERIOR_X_COLUMN],
                           EXTERIOR_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.EXTERIOR_Y_COLUMN],
                           EXTERIOR_VERTEX_Y_METRES, atol=TOLERANCE))

        self.assertTrue(
            len(this_vertex_dict[polygons.HOLE_X_COLUMN]) == NUM_HOLES)
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_X_COLUMN][0],
                           HOLE1_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_Y_COLUMN][0],
                           HOLE1_VERTEX_Y_METRES, atol=TOLERANCE))

        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_X_COLUMN][1],
                           HOLE2_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_Y_COLUMN][1],
                           HOLE2_VERTEX_Y_METRES, atol=TOLERANCE))

    def test_merge_exterior_and_holes(self):
        """Ensures correct output from _merge_exterior_and_holes."""

        (this_vertex_x_metres,
         this_vertex_y_metres) = polygons._merge_exterior_and_holes(
            EXTERIOR_VERTEX_X_METRES, EXTERIOR_VERTEX_Y_METRES,
            hole_x_vertex_metres_list=[HOLE1_VERTEX_X_METRES,
                                       HOLE2_VERTEX_X_METRES],
            hole_y_vertex_metres_list=[HOLE1_VERTEX_Y_METRES,
                                       HOLE2_VERTEX_Y_METRES])

        self.assertTrue(
            numpy.allclose(this_vertex_x_metres, MERGED_VERTEX_X_METRES,
                           atol=TOLERANCE, equal_nan=True))
        self.assertTrue(
            numpy.allclose(this_vertex_y_metres, MERGED_VERTEX_Y_METRES,
                           atol=TOLERANCE, equal_nan=True))

    def text_vertex_arrays_to_list(self):
        """Ensures correct output from _vertex_arrays_to_list."""

        this_vertex_metres_list = polygons._vertex_arrays_to_list(
            MERGED_VERTEX_X_METRES, MERGED_VERTEX_Y_METRES)

        self.assertTrue(
            len(this_vertex_metres_list) == len(MERGED_VERTEX_METRES_LIST))

        for i in range(len(MERGED_VERTEX_METRES_LIST)):
            self.assertTrue(
                numpy.allclose(numpy.asarray(this_vertex_metres_list[i]),
                               numpy.asarray(MERGED_VERTEX_METRES_LIST[i]),
                               atol=TOLERANCE, equal_nan=True))

    def test_vertex_list_to_arrays(self):
        """Ensures correct output from _vertex_list_to_arrays."""

        (this_vertex_x_metres,
         this_vertex_y_metres) = polygons._vertex_list_to_arrays(
            MERGED_VERTEX_METRES_LIST)

        self.assertTrue(
            numpy.allclose(this_vertex_x_metres, MERGED_VERTEX_X_METRES,
                           atol=TOLERANCE, equal_nan=True))
        self.assertTrue(
            numpy.allclose(this_vertex_y_metres, MERGED_VERTEX_Y_METRES,
                           atol=TOLERANCE, equal_nan=True))

    def test_vertices_to_polygon_object(self):
        """Ensures correct output from _vertices_to_polygon_object.

        This is not strictly a unit test.  _vertices_to_polygon_object is used
        to convert to a polygon object, and then _polygon_object_to_vertices is
        used to convert back to vertex arrays.  The output of
        _polygon_object_to_vertices is compared with the input to
        _vertices_to_polygon_object, and both sets of vertex arrays must be
        equal.
        """

        this_polygon_object = polygons._vertices_to_polygon_object(
            EXTERIOR_VERTEX_X_METRES, EXTERIOR_VERTEX_Y_METRES,
            hole_x_vertex_metres_list=[HOLE1_VERTEX_X_METRES,
                                       HOLE2_VERTEX_X_METRES],
            hole_y_vertex_metres_list=[HOLE1_VERTEX_Y_METRES,
                                       HOLE2_VERTEX_Y_METRES])

        this_vertex_dict = polygons._polygon_object_to_vertices(
            this_polygon_object)

        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.EXTERIOR_X_COLUMN],
                           EXTERIOR_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.EXTERIOR_Y_COLUMN],
                           EXTERIOR_VERTEX_Y_METRES, atol=TOLERANCE))

        self.assertTrue(
            len(this_vertex_dict[polygons.HOLE_X_COLUMN]) == NUM_HOLES)
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_X_COLUMN][0],
                           HOLE1_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_Y_COLUMN][0],
                           HOLE1_VERTEX_Y_METRES, atol=TOLERANCE))

        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_X_COLUMN][1],
                           HOLE2_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_Y_COLUMN][1],
                           HOLE2_VERTEX_Y_METRES, atol=TOLERANCE))

    def test_polygon_object_to_vertices(self):
        """Ensures correct output from _polygon_object_to_vertices."""

        this_vertex_dict = polygons._polygon_object_to_vertices(POLYGON_OBJECT)

        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.EXTERIOR_X_COLUMN],
                           EXTERIOR_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.EXTERIOR_Y_COLUMN],
                           EXTERIOR_VERTEX_Y_METRES, atol=TOLERANCE))

        self.assertTrue(
            len(this_vertex_dict[polygons.HOLE_X_COLUMN]) == NUM_HOLES)
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_X_COLUMN][0],
                           HOLE1_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_Y_COLUMN][0],
                           HOLE1_VERTEX_Y_METRES, atol=TOLERANCE))

        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_X_COLUMN][1],
                           HOLE2_VERTEX_X_METRES, atol=TOLERANCE))
        self.assertTrue(
            numpy.allclose(this_vertex_dict[polygons.HOLE_Y_COLUMN][1],
                           HOLE2_VERTEX_Y_METRES, atol=TOLERANCE))

    def test_get_direction_of_vertex_pair_up(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is up.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_UP, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_UP)
        self.assertTrue(this_direction == polygons.UP_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_down(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is down.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_DOWN, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_DOWN)
        self.assertTrue(this_direction == polygons.DOWN_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_right(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is right.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_RIGHT, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_RIGHT)
        self.assertTrue(this_direction == polygons.RIGHT_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_left(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is left.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_LEFT, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_LEFT)
        self.assertTrue(this_direction == polygons.LEFT_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_up_right(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is up and right.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_UP_RIGHT, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_UP_RIGHT)
        self.assertTrue(this_direction == polygons.UP_RIGHT_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_up_left(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is up and left.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_UP_LEFT, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_UP_LEFT)
        self.assertTrue(this_direction == polygons.UP_LEFT_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_down_right(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is down and right.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_DOWN_RIGHT, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_DOWN_RIGHT)
        self.assertTrue(this_direction == polygons.DOWN_RIGHT_DIRECTION_NAME)

    def test_get_direction_of_vertex_pair_down_left(self):
        """Ensures correct output from _get_direction_of_vertex_pair.

        In this case, direction from first to second vertex is down and left.
        """

        this_direction = polygons._get_direction_of_vertex_pair(
            FIRST_VERTEX_ROW, SECOND_VERTEX_ROW_DOWN_LEFT, FIRST_VERTEX_COLUMN,
            SECOND_VERTEX_COLUMN_DOWN_LEFT)
        self.assertTrue(this_direction == polygons.DOWN_LEFT_DIRECTION_NAME)

    def test_remove_redundant_vertices(self):
        """Ensures correct output from _remove_redundant_vertices."""

        (these_vertex_rows,
         these_vertex_columns) = polygons._remove_redundant_vertices(
            VERTEX_ROWS_GRID_CELL_EDGES_REDUNDANT,
            VERTEX_COLUMNS_GRID_CELL_EDGES_REDUNDANT)

        self.assertTrue(
            numpy.array_equal(these_vertex_rows,
                              VERTEX_ROWS_GRID_CELL_EDGES_NON_REDUNDANT))
        self.assertTrue(
            numpy.array_equal(these_vertex_columns,
                              VERTEX_COLUMNS_GRID_CELL_EDGES_NON_REDUNDANT))

    def test_points_in_poly_to_binary_matrix(self):
        """Ensures correct output from _points_in_poly_to_binary_matrix."""

        (this_point_in_polygon_matrix, this_first_row_index,
         this_first_column_index) = polygons._points_in_poly_to_binary_matrix(
            ROW_INDICES_IN_POLYGON, COLUMN_INDICES_IN_POLYGON)

        self.assertTrue(numpy.array_equal(this_point_in_polygon_matrix,
                                          POINT_IN_POLYGON_MATRIX))
        self.assertTrue(this_first_row_index == FIRST_ROW_INDEX)
        self.assertTrue(this_first_column_index == FIRST_COLUMN_INDEX)

    def test_binary_matrix_to_points_in_poly(self):
        """Ensures correct output from _binary_matrix_to_points_in_poly."""

        (these_row_indices,
         these_column_indices) = polygons._binary_matrix_to_points_in_poly(
            POINT_IN_POLYGON_MATRIX, FIRST_ROW_INDEX, FIRST_COLUMN_INDEX)

        self.assertTrue(
            numpy.array_equal(these_row_indices, ROW_INDICES_IN_POLYGON))
        self.assertTrue(
            numpy.array_equal(these_column_indices, COLUMN_INDICES_IN_POLYGON))

    def test_adjust_vertices_to_grid_cell_edges(self):
        """This is an integration test.

        Ensures correct output from _adjust_vertices_to_grid_cell_edges and
        _remove_redundant_vertices.  This makes more sense than testing
        _adjust_vertices_to_grid_cell_edges alone, because the expected output
        is hard to define (it involves redundant pairs of vertices, and it is
        hard to determine a priori what the redundant set will be).
        """

        (these_vertex_rows_redundant,
         these_vertex_columns_redundant) = (
            polygons._adjust_vertices_to_grid_cell_edges(
                VERTEX_ROWS_GRID_POINTS, VERTEX_COLUMNS_GRID_POINTS))

        (these_vertex_rows_non_redundant,
         these_vertex_columns_non_redundant) = (
            polygons._remove_redundant_vertices(these_vertex_rows_redundant,
                                                these_vertex_columns_redundant))

        self.assertTrue(
            numpy.array_equal(these_vertex_rows_non_redundant,
                              VERTEX_ROWS_GRID_CELL_EDGES_NON_REDUNDANT))
        self.assertTrue(
            numpy.array_equal(these_vertex_columns_non_redundant,
                              VERTEX_COLUMNS_GRID_CELL_EDGES_NON_REDUNDANT))

    def test_points_in_poly_to_vertices(self):
        """Ensures correct output from points_in_poly_to_vertices."""

        (these_vertex_rows,
         these_vertex_columns) = polygons.points_in_poly_to_vertices(
            ROW_INDICES_IN_POLYGON, COLUMN_INDICES_IN_POLYGON)

        self.assertTrue(
            numpy.array_equal(these_vertex_rows,
                              VERTEX_ROWS_GRID_CELL_EDGES_NON_REDUNDANT))
        self.assertTrue(
            numpy.array_equal(these_vertex_columns,
                              VERTEX_COLUMNS_GRID_CELL_EDGES_NON_REDUNDANT))

    def test_make_buffer_around_simple_polygon_small(self):
        """Ensures correct output from make_buffer_around_simple_polygon.

        In this case, using smaller of the two buffer distances.
        """

        (this_buffer_vertex_x_metres, this_buffer_vertex_y_metres) = (
            polygons.make_buffer_around_simple_polygon(
                EXTERIOR_VERTEX_X_METRES, EXTERIOR_VERTEX_Y_METRES,
                max_buffer_dist_metres=SMALL_BUFFER_DIST_METRES,
                preserve_angles=True))

        self.assertTrue(numpy.allclose(this_buffer_vertex_x_metres,
                                       VERTEX_X_METRES_SMALL_BUFFER,
                                       atol=TOLERANCE))
        self.assertTrue(numpy.allclose(this_buffer_vertex_y_metres,
                                       VERTEX_Y_METRES_SMALL_BUFFER,
                                       atol=TOLERANCE))

    def test_make_buffer_around_simple_polygon_large(self):
        """Ensures correct output from make_buffer_around_simple_polygon.

        In this case, using larger of the two buffer distances.
        """

        (this_buffer_vertex_x_metres, this_buffer_vertex_y_metres) = (
            polygons.make_buffer_around_simple_polygon(
                EXTERIOR_VERTEX_X_METRES, EXTERIOR_VERTEX_Y_METRES,
                max_buffer_dist_metres=LARGE_BUFFER_DIST_METRES,
                preserve_angles=True))

        self.assertTrue(numpy.allclose(this_buffer_vertex_x_metres,
                                       VERTEX_X_METRES_LARGE_BUFFER,
                                       atol=TOLERANCE))
        self.assertTrue(numpy.allclose(this_buffer_vertex_y_metres,
                                       VERTEX_Y_METRES_LARGE_BUFFER,
                                       atol=TOLERANCE))

    def test_make_buffer_around_simple_polygon_nested(self):
        """Ensures correct output from make_buffer_around_simple_polygon.

        In this case, using two buffer distances (one to create exterior of
        polygon, one to create hole).
        """

        (this_buffer_vertex_x_metres, this_buffer_vertex_y_metres) = (
            polygons.make_buffer_around_simple_polygon(
                EXTERIOR_VERTEX_X_METRES, EXTERIOR_VERTEX_Y_METRES,
                min_buffer_dist_metres=SMALL_BUFFER_DIST_METRES,
                max_buffer_dist_metres=LARGE_BUFFER_DIST_METRES,
                preserve_angles=True))

        self.assertTrue(numpy.allclose(this_buffer_vertex_x_metres,
                                       VERTEX_X_METRES_NESTED_BUFFER,
                                       atol=TOLERANCE, equal_nan=True))
        self.assertTrue(numpy.allclose(this_buffer_vertex_y_metres,
                                       VERTEX_Y_METRES_NESTED_BUFFER,
                                       atol=TOLERANCE, equal_nan=True))


if __name__ == '__main__':
    unittest.main()