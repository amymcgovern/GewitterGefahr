"""Plotting methods for linkage.

--- DEFINITIONS ---

Linkage = association of a storm cell with other phenomena (e.g., wind
observations).  See link_storms_to_winds.py.
"""

import numpy
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import polygons
from gewittergefahr.gg_utils import error_checking
from gewittergefahr.plotting import storm_plotting
from gewittergefahr.plotting import wind_plotting
from gewittergefahr.gg_utils import link_storms_to_winds as storms_to_winds


def plot_one_storm_cell_to_winds(
        storm_to_winds_table, storm_id, basemap_object=None, axes_object=None,
        storm_colour=storm_plotting.DEFAULT_TRACK_COLOUR,
        storm_line_width=storm_plotting.DEFAULT_TRACK_WIDTH,
        wind_barb_length=wind_plotting.DEFAULT_BARB_LENGTH,
        empty_wind_barb_radius=wind_plotting.DEFAULT_EMPTY_BARB_RADIUS,
        fill_empty_wind_barb=wind_plotting.FILL_EMPTY_BARB_DEFAULT,
        wind_colour_map=wind_plotting.DEFAULT_COLOUR_MAP,
        colour_minimum_kt=wind_plotting.DEFAULT_COLOUR_MINIMUM_KT,
        colour_maximum_kt=wind_plotting.DEFAULT_COLOUR_MAXIMUM_KT):
    """Plots wind observations linked to one storm cell.

    :param storm_to_winds_table: pandas DataFrame with columns documented in
        `link_storms_to_winds.write_storm_to_winds_table`.
    :param storm_id: String ID for storm cell.  Only this storm cell and wind
        observations linked thereto will be plotted.
    :param basemap_object: Instance of `mpl_toolkits.basemap.Basemap`.
    :param axes_object: Instance of `matplotlib.axes._subplots.AxesSubplot`.
    :param storm_colour: Colour for storm track, first storm object, and last
        storm object (in any format accepted by `matplotlib.colors`).
    :param storm_line_width: Line width for storm track, first storm object, and
        last storm object (real positive number).
    :param wind_barb_length: Length of each wind barb.
    :param empty_wind_barb_radius: Radius of circle for 0-metre-per-second wind
        barb.
    :param fill_empty_wind_barb: Boolean flag.  If fill_empty_barb = True,
        0-metre-per-second wind barb will be a filled circle.  Otherwise, it
        will be an empty circle.
    :param wind_colour_map: Instance of `matplotlib.pyplot.cm`.
    :param colour_minimum_kt: Minimum speed for colour map (kt or nautical miles
        per hour).
    :param colour_maximum_kt: Maximum speed for colour map (kt or nautical miles
        per hour).
    """

    error_checking.assert_is_string(storm_id)
    error_checking.assert_is_geq(colour_minimum_kt, 0.)
    error_checking.assert_is_greater(colour_maximum_kt, colour_minimum_kt)

    storm_cell_flags = [this_id == storm_id for this_id in storm_to_winds_table[
        tracking_io.STORM_ID_COLUMN].values]
    storm_cell_rows = numpy.where(numpy.array(storm_cell_flags))[0]

    centroid_latitudes_deg = storm_to_winds_table[
        tracking_io.CENTROID_LAT_COLUMN].values[storm_cell_rows]
    centroid_longitudes_deg = storm_to_winds_table[
        tracking_io.CENTROID_LNG_COLUMN].values[storm_cell_rows]

    storm_plotting.plot_storm_track(
        basemap_object=basemap_object, axes_object=axes_object,
        latitudes_deg=centroid_latitudes_deg,
        longitudes_deg=centroid_longitudes_deg, line_colour=storm_colour,
        line_width=storm_line_width)

    storm_times_unix_sec = storm_to_winds_table[tracking_io.TIME_COLUMN].values[
        storm_cell_rows]
    first_storm_object_row = storm_cell_rows[numpy.argmin(storm_times_unix_sec)]
    last_storm_object_row = storm_cell_rows[numpy.argmax(storm_times_unix_sec)]

    first_vertex_dict = polygons.polygon_object_to_vertex_arrays(
        storm_to_winds_table[tracking_io.POLYGON_OBJECT_LATLNG_COLUMN].values[
            first_storm_object_row])
    first_vertex_latitudes_deg = first_vertex_dict[polygons.EXTERIOR_Y_COLUMN]
    first_vertex_longitudes_deg = first_vertex_dict[polygons.EXTERIOR_X_COLUMN]

    storm_plotting.plot_unfilled_polygon(
        basemap_object=basemap_object, axes_object=axes_object,
        vertex_latitudes_deg=first_vertex_latitudes_deg,
        vertex_longitudes_deg=first_vertex_longitudes_deg,
        exterior_colour=storm_colour, exterior_line_width=storm_line_width)

    last_vertex_dict = polygons.polygon_object_to_vertex_arrays(
        storm_to_winds_table[tracking_io.POLYGON_OBJECT_LATLNG_COLUMN].values[
            last_storm_object_row])
    last_vertex_latitudes_deg = last_vertex_dict[polygons.EXTERIOR_Y_COLUMN]
    last_vertex_longitudes_deg = last_vertex_dict[polygons.EXTERIOR_X_COLUMN]

    storm_plotting.plot_unfilled_polygon(
        basemap_object=basemap_object, axes_object=axes_object,
        vertex_latitudes_deg=last_vertex_latitudes_deg,
        vertex_longitudes_deg=last_vertex_longitudes_deg,
        exterior_colour=storm_colour, exterior_line_width=storm_line_width)

    wind_latitudes_deg = numpy.array([])
    wind_longitudes_deg = numpy.array([])
    u_winds_m_s01 = numpy.array([])
    v_winds_m_s01 = numpy.array([])

    for this_row in storm_cell_rows:
        wind_latitudes_deg = numpy.concatenate((
            wind_latitudes_deg, storm_to_winds_table[
                storms_to_winds.WIND_LATITUDES_COLUMN].values[this_row]))
        wind_longitudes_deg = numpy.concatenate((
            wind_longitudes_deg, storm_to_winds_table[
                storms_to_winds.WIND_LONGITUDES_COLUMN].values[this_row]))
        u_winds_m_s01 = numpy.concatenate((
            u_winds_m_s01, storm_to_winds_table[
                storms_to_winds.U_WINDS_COLUMN].values[this_row]))
        v_winds_m_s01 = numpy.concatenate((
            v_winds_m_s01, storm_to_winds_table[
                storms_to_winds.V_WINDS_COLUMN].values[this_row]))

    wind_plotting.plot_wind_barbs(
        basemap_object=basemap_object, axes_object=axes_object,
        latitudes_deg=wind_latitudes_deg, longitudes_deg=wind_longitudes_deg,
        u_winds_m_s01=u_winds_m_s01, v_winds_m_s01=v_winds_m_s01,
        barb_length=wind_barb_length, empty_barb_radius=empty_wind_barb_radius,
        fill_empty_barb=fill_empty_wind_barb, colour_map=wind_colour_map,
        colour_minimum_kt=colour_minimum_kt,
        colour_maximum_kt=colour_maximum_kt)
