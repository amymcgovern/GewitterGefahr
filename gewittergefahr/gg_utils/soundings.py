"""Methods for creating and analyzing soundings."""

import os.path
import numpy
import pandas
from sharppy.sharptab import params as sharppy_params
from sharppy.sharptab import winds as sharppy_winds
from sharppy.sharptab import interp as sharppy_interp
from sharppy.sharptab import profile as sharppy_profile
from sharppy.sharptab import utils as sharppy_utils
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import moisture_conversions
from gewittergefahr.gg_utils import temperature_conversions
from gewittergefahr.gg_utils import interp
from gewittergefahr.gg_utils import nwp_model_utils
from gewittergefahr.gg_utils import error_checking

TEMPORAL_INTERP_METHOD = interp.PREVIOUS_INTERP_METHOD
SPATIAL_INTERP_METHOD = interp.NEAREST_INTERP_METHOD

SENTINEL_VALUE_FOR_SHARPPY = -9999.
REDUNDANT_PRESSURE_TOLERANCE_MB = 1e-3
REDUNDANT_HEIGHT_TOLERANCE_METRES = 1e-3

PERCENT_TO_UNITLESS = 0.01
PASCALS_TO_MB = 0.01
MB_TO_PASCALS = 100
METRES_PER_SECOND_TO_KT = 3.6 / 1.852
KT_TO_METRES_PER_SECOND = 1.852 / 3.6

PRESSURE_COLUMN_FOR_SHARPPY = 'pressure_mb'
HEIGHT_COLUMN_FOR_SHARPPY = 'geopotential_height_metres'
TEMPERATURE_COLUMN_FOR_SHARPPY = 'temperature_deg_c'
DEWPOINT_COLUMN_FOR_SHARPPY = 'dewpoint_deg_c'
U_WIND_COLUMN_FOR_SHARPPY = 'u_wind_kt'
V_WIND_COLUMN_FOR_SHARPPY = 'v_wind_kt'
IS_SURFACE_COLUMN = 'is_surface'

CONVECTIVE_TEMPERATURE_NAME = 'convective_temperature_kelvins'
HELICITY_NAMES_SHARPPY = ['srh1km', 'srh3km', 'left_esrh', 'right_esrh']
SHARPPY_NAMES_FOR_MASKED_WIND_ARRAYS = [
    'mean_1km', 'mean_3km', 'mean_6km', 'mean_8km', 'mean_lcl_el']

SI_NAME_COLUMN = 'sounding_index_name'
SI_NAME_COLUMN_SHARPPY = 'sounding_index_name_sharppy'
CONVERSION_FACTOR_COLUMN = 'conversion_factor'
IS_VECTOR_COLUMN = 'is_vector'
IN_MUPCL_OBJECT_COLUMN = 'in_mupcl_object'

METAFILE_NAME_FOR_SOUNDING_INDICES = os.path.join(
    os.path.dirname(__file__), 'sounding_index_metadata.csv')

SI_METADATA_COLUMNS = [
    SI_NAME_COLUMN, SI_NAME_COLUMN_SHARPPY, CONVERSION_FACTOR_COLUMN,
    IS_VECTOR_COLUMN, IN_MUPCL_OBJECT_COLUMN]

METADATA_COLUMN_TYPE_DICT = {
    SI_NAME_COLUMN: str, SI_NAME_COLUMN_SHARPPY: str,
    CONVERSION_FACTOR_COLUMN: numpy.float64, IS_VECTOR_COLUMN: bool,
    IN_MUPCL_OBJECT_COLUMN: bool}

X_COMPONENT_SUFFIX = 'x'
Y_COMPONENT_SUFFIX = 'y'
MAGNITUDE_SUFFIX = 'magnitude'
COSINE_SUFFIX = 'cos'
SINE_SUFFIX = 'sin'


def _get_nwp_fields_in_sounding(model_name, minimum_pressure_mb=0.,
                                return_dict=False):
    """Returns list of NWP fields needed to create sounding.

    Each "sounding field" is one variable at one pressure level (e.g.,
    500-mb height, 600-mb specific humidity, 700-mb temperature, etc.).

    N = number of sounding fields
    P = number of pressure levels

    :param model_name: Name of model.
    :param minimum_pressure_mb: Minimum pressure (millibars).  All sounding
        fields from a lower pressure will be ignored (excluded from list).
    :param return_dict: Boolean flag.  If True, this method returns
        `sounding_table_to_fields_dict` and `pressure_levels_mb`.  If False,
        returns `sounding_field_names` and `sounding_field_names_grib1`.
    :return: sounding_field_names: length-N list of field names in
        GewitterGefahr format.
    :return: sounding_field_names_grib1: length-N list of field names in grib1
        format.
    :return: sounding_table_to_fields_dict: Dictionary with the following keys.
    sounding_table_to_fields_dict['geopotential_height_metres']: length-P list
        of height fields in `sounding_field_names`.
    sounding_table_to_fields_dict['temperature_kelvins']: length-P list of
        temperature fields in `sounding_field_names`.
    sounding_table_to_fields_dict['humidity']: length-P list of humidity fields
        in `sounding_field_names`.
    sounding_table_to_fields_dict['u_wind_m_s01']: length-P list of u-wind
        fields in `sounding_field_names`.
    sounding_table_to_fields_dict['v_wind_m_s01']: length-P list of v-wind
        fields in `sounding_field_names`.

    :return: pressure_levels_mb: length-P numpy array of pressure levels
        (millibars).
    """

    nwp_model_utils.check_model_name(model_name)
    error_checking.assert_is_geq(minimum_pressure_mb, 0)
    error_checking.assert_is_boolean(return_dict)

    pressure_levels_mb = nwp_model_utils.get_pressure_levels(model_name)
    pressure_levels_mb = pressure_levels_mb[
        pressure_levels_mb >= minimum_pressure_mb]
    num_pressure_levels = len(pressure_levels_mb)

    sounding_table_columns, sounding_table_columns_grib1 = (
        nwp_model_utils.get_columns_in_sounding_table(model_name))
    num_sounding_table_columns = len(sounding_table_columns)

    if return_dict:
        sounding_table_to_fields_dict = {}
        for j in range(num_sounding_table_columns):
            sounding_table_to_fields_dict.update(
                {sounding_table_columns[j]: []})
    else:
        sounding_field_names = []
        sounding_field_names_grib1 = []

    for j in range(num_sounding_table_columns):
        for k in range(num_pressure_levels):
            this_field_name = '{0:s}_{1:d}mb'.format(
                sounding_table_columns[j], int(pressure_levels_mb[k]))

            if return_dict:
                sounding_table_to_fields_dict[sounding_table_columns[j]].append(
                    this_field_name)
            else:
                sounding_field_names.append(this_field_name)
                sounding_field_names_grib1.append('{0:s}:{1:d} mb'.format(
                    sounding_table_columns_grib1[j],
                    int(pressure_levels_mb[k])))

        if sounding_table_columns[
                j] == nwp_model_utils.TEMPERATURE_COLUMN_FOR_SOUNDING_TABLES:
            this_field_name, this_field_name_grib1 = (
                nwp_model_utils.get_lowest_temperature_name(model_name))

        elif sounding_table_columns[j] in [
                nwp_model_utils.RH_COLUMN_FOR_SOUNDING_TABLES,
                nwp_model_utils.SPFH_COLUMN_FOR_SOUNDING_TABLES]:
            this_field_name, this_field_name_grib1 = (
                nwp_model_utils.get_lowest_humidity_name(model_name))

        elif sounding_table_columns[
                j] == nwp_model_utils.HEIGHT_COLUMN_FOR_SOUNDING_TABLES:
            this_field_name, this_field_name_grib1 = (
                nwp_model_utils.get_lowest_height_name(model_name))

        elif sounding_table_columns[
                j] == nwp_model_utils.U_WIND_COLUMN_FOR_SOUNDING_TABLES:
            this_field_name, this_field_name_grib1 = (
                nwp_model_utils.get_lowest_u_wind_name(model_name))

        elif sounding_table_columns[
                j] == nwp_model_utils.V_WIND_COLUMN_FOR_SOUNDING_TABLES:
            this_field_name, this_field_name_grib1 = (
                nwp_model_utils.get_lowest_v_wind_name(model_name))

        if return_dict:
            sounding_table_to_fields_dict[sounding_table_columns[j]].append(
                this_field_name)
        else:
            sounding_field_names.append(this_field_name)
            sounding_field_names_grib1.append(this_field_name_grib1)

    if return_dict:
        return sounding_table_to_fields_dict, pressure_levels_mb

    this_field_name, this_field_name_grib1 = (
        nwp_model_utils.get_lowest_pressure_name(model_name))
    sounding_field_names.append(this_field_name)
    sounding_field_names_grib1.append(this_field_name_grib1)

    return sounding_field_names, sounding_field_names_grib1


def _remove_subsurface_sounding_data(sounding_table, delete_rows=None):
    """Removes sounding data from levels below the surface.

    :param sounding_table: See documentation for
        get_sounding_indices_from_sharppy.
    :param delete_rows: Boolean flag.  If True, will delete all subsurface rows
        except 1000 mb (where temperature/dewpoint/u-wind/v-wind will be set to
        sentinel value).  If False, will set temperature/dewpoint/u-wind/v-wind
        in subsurface rows to sentinel value.
    :return: sounding_table: Same as input, except:
        [1] Some rows may have been removed.
        [2] Some temperatures/dewpoints/u-winds/v-winds may have been set to
            sentinel value.
    """

    surface_row = numpy.where(sounding_table[IS_SURFACE_COLUMN].values)[0][0]

    surface_height_m_asl = sounding_table[
        HEIGHT_COLUMN_FOR_SHARPPY].values[surface_row]
    subsurface_flags = (
        sounding_table[HEIGHT_COLUMN_FOR_SHARPPY].values < surface_height_m_asl)
    subsurface_rows = numpy.where(subsurface_flags)[0]

    if delete_rows:
        pressure_1000mb_flags = sounding_table[
            PRESSURE_COLUMN_FOR_SHARPPY].values == 1000
        bad_flags = numpy.logical_and(
            subsurface_flags, numpy.invert(pressure_1000mb_flags))

        bad_rows = numpy.where(bad_flags)[0]
        sounding_table = sounding_table.drop(
            sounding_table.index[bad_rows], axis=0, inplace=False).reset_index(
                drop=True)

        subsurface_flags = (
            sounding_table[HEIGHT_COLUMN_FOR_SHARPPY].values <
            surface_height_m_asl)
        subsurface_rows = numpy.where(subsurface_flags)[0]

    sounding_table[TEMPERATURE_COLUMN_FOR_SHARPPY].values[
        subsurface_rows] = SENTINEL_VALUE_FOR_SHARPPY
    sounding_table[DEWPOINT_COLUMN_FOR_SHARPPY].values[
        subsurface_rows] = SENTINEL_VALUE_FOR_SHARPPY
    sounding_table[U_WIND_COLUMN_FOR_SHARPPY].values[
        subsurface_rows] = SENTINEL_VALUE_FOR_SHARPPY
    sounding_table[V_WIND_COLUMN_FOR_SHARPPY].values[
        subsurface_rows] = SENTINEL_VALUE_FOR_SHARPPY

    return sounding_table


def _sort_sounding_by_height(sounding_table):
    """Sorts rows in sounding table by increasing height.

    :param sounding_table: See documentation for
        get_sounding_indices_from_sharppy.
    :return: sounding_table: Same as input, except row order.
    """

    return sounding_table.sort_values(
        HEIGHT_COLUMN_FOR_SHARPPY, axis=0, ascending=True, inplace=False)


def _remove_redundant_sounding_data(sorted_sounding_table):
    """If surface is very close to first level above, removes surface data.

    :param sorted_sounding_table: See documentation for
        _sort_sounding_by_height.
    :return: sorted_sounding_table: Same as input, except that, if redundant,
        surface temperature/dewpoint/u-wind/v-wind have been changed to sentinel
        value.
    """

    surface_row = numpy.where(
        sorted_sounding_table[IS_SURFACE_COLUMN].values)[0][0]

    height_diff_metres = (
        sorted_sounding_table[HEIGHT_COLUMN_FOR_SHARPPY].values[
            surface_row + 1] -
        sorted_sounding_table[HEIGHT_COLUMN_FOR_SHARPPY].values[
            surface_row])
    pressure_diff_mb = numpy.absolute(
        sorted_sounding_table[PRESSURE_COLUMN_FOR_SHARPPY].values[
            surface_row + 1] -
        sorted_sounding_table[PRESSURE_COLUMN_FOR_SHARPPY].values[
            surface_row])

    if (height_diff_metres >= REDUNDANT_HEIGHT_TOLERANCE_METRES and
            pressure_diff_mb >= REDUNDANT_PRESSURE_TOLERANCE_MB):
        return sorted_sounding_table

    sorted_sounding_table[TEMPERATURE_COLUMN_FOR_SHARPPY].values[
        surface_row] = SENTINEL_VALUE_FOR_SHARPPY
    sorted_sounding_table[DEWPOINT_COLUMN_FOR_SHARPPY].values[
        surface_row] = SENTINEL_VALUE_FOR_SHARPPY
    sorted_sounding_table[U_WIND_COLUMN_FOR_SHARPPY].values[
        surface_row] = SENTINEL_VALUE_FOR_SHARPPY
    sorted_sounding_table[V_WIND_COLUMN_FOR_SHARPPY].values[
        surface_row] = SENTINEL_VALUE_FOR_SHARPPY
    return sorted_sounding_table


def _adjust_srw_for_storm_motion(profile_object, eastward_motion_kt=None,
                                 northward_motion_kt=None):
    """Adjust storm-relative winds to account for storm motion.

    This method works on a single sounding (profile_object).

    :param profile_object: Instance of `sharppy.sharptab.Profile`.
    :param eastward_motion_kt: u-component of storm motion (knots).
    :param northward_motion_kt: v-component of storm motion (knots).
    :return: profile_object: Same as input, but with different storm-relative
        winds.
    """

    surface_pressure_mb = profile_object.pres[profile_object.sfc]
    pressure_at_1km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 1000.))
    pressure_at_2km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 2000.))
    pressure_at_3km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 3000.))
    pressure_at_4km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 4000.))
    pressure_at_5km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 5000.))
    pressure_at_6km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 6000.))
    pressure_at_8km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 8000.))
    pressure_at_9km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 9000.))
    pressure_at_11km_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(profile_object, 11000.))

    this_depth_metres = (profile_object.mupcl.elhght - profile_object.ebotm) / 2
    effective_bulk_layer_top_mb = sharppy_interp.pres(
        profile_object, sharppy_interp.to_msl(
            profile_object, profile_object.ebotm + this_depth_metres))

    profile_object.srw_1km = sharppy_winds.sr_wind(
        profile_object, pbot=surface_pressure_mb, ptop=pressure_at_1km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_0_2km = sharppy_winds.sr_wind(
        profile_object, pbot=surface_pressure_mb, ptop=pressure_at_2km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_3km = sharppy_winds.sr_wind(
        profile_object, pbot=surface_pressure_mb, ptop=pressure_at_3km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_6km = sharppy_winds.sr_wind(
        profile_object, pbot=surface_pressure_mb, ptop=pressure_at_6km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_8km = sharppy_winds.sr_wind(
        profile_object, pbot=surface_pressure_mb, ptop=pressure_at_8km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_4_5km = sharppy_winds.sr_wind(
        profile_object, pbot=pressure_at_4km_mb, ptop=pressure_at_5km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_4_6km = sharppy_winds.sr_wind(
        profile_object, pbot=pressure_at_4km_mb, ptop=pressure_at_6km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_9_11km = sharppy_winds.sr_wind(
        profile_object, pbot=pressure_at_9km_mb, ptop=pressure_at_11km_mb,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_ebw = sharppy_winds.sr_wind(
        profile_object, pbot=profile_object.ebottom,
        ptop=effective_bulk_layer_top_mb, stu=eastward_motion_kt,
        stv=northward_motion_kt)
    profile_object.srw_eff = sharppy_winds.sr_wind(
        profile_object, pbot=profile_object.ebottom, ptop=profile_object.etop,
        stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srw_lcl_el = sharppy_winds.sr_wind(
        profile_object, pbot=profile_object.mupcl.lclpres,
        ptop=profile_object.mupcl.elpres, stu=eastward_motion_kt,
        stv=northward_motion_kt)

    return profile_object


def _adjust_sounding_indices_for_storm_motion(profile_object,
                                              eastward_motion_kt=None,
                                              northward_motion_kt=None):
    """Adjust sounding indices to account for storm motion.

    This method works on a single sounding (profile_object).

    :param profile_object: Instance of `sharppy.sharptab.Profile`.
    :param eastward_motion_kt: u-component of storm motion (knots).
    :param northward_motion_kt: v-component of storm motion (knots).
    :return: profile_object: Same as input, except for sounding indices that
        depend on storm motion.
    """

    profile_object = _adjust_srw_for_storm_motion(
        profile_object, eastward_motion_kt=eastward_motion_kt,
        northward_motion_kt=northward_motion_kt)

    profile_object.critical_angle = sharppy_winds.critical_angle(
        profile_object, stu=eastward_motion_kt, stv=northward_motion_kt)
    profile_object.srh1km = sharppy_winds.helicity(
        profile_object, 0., 1000., stu=eastward_motion_kt,
        stv=northward_motion_kt)
    profile_object.srh3km = sharppy_winds.helicity(
        profile_object, 0., 3000., stu=eastward_motion_kt,
        stv=northward_motion_kt)
    profile_object.ehi1km = sharppy_params.ehi(
        profile_object, profile_object.mupcl, 0., 1000., stu=eastward_motion_kt,
        stv=northward_motion_kt)
    profile_object.ehi3km = sharppy_params.ehi(
        profile_object, profile_object.mupcl, 0., 3000., stu=eastward_motion_kt,
        stv=northward_motion_kt)

    effective_layer_srh_j_kg01 = sharppy_winds.helicity(
        profile_object, profile_object.ebotm, profile_object.etopm,
        stu=eastward_motion_kt, stv=northward_motion_kt)[1]
    profile_object.stp_cin = sharppy_params.stp_cin(
        profile_object.mlpcl.bplus, effective_layer_srh_j_kg01,
        profile_object.ebwspd * KT_TO_METRES_PER_SECOND,
        profile_object.mlpcl.lclhght, profile_object.mlpcl.bminus)

    this_shear_magnitude_m_s01 = KT_TO_METRES_PER_SECOND * numpy.sqrt(
        profile_object.sfc_6km_shear[0] ** 2 +
        profile_object.sfc_6km_shear[1] ** 2)
    profile_object.stp_fixed = sharppy_params.stp_fixed(
        profile_object.sfcpcl.bplus, profile_object.sfcpcl.lclhght,
        profile_object.srh1km[0], this_shear_magnitude_m_s01)

    profile_object.get_traj()  # Recomputes updraft tilt.
    return profile_object


def _fix_sharppy_wind_vector(sharppy_wind_vector):
    """Converts SHARPpy wind vector.

    SHARPpy format = masked array with direction/magnitude
    New format = normal numpy array with u- and v-components

    SHARPpy creates masked arrays only for mean wind from 0-1 km AGL,
    0-3 km AGL, 0-6 km AGL, 0-8 km AGL, and lifting condensation level
    - equilibrium level.  Why??

    :param sharppy_wind_vector: Wind vector in SHARPpy format.
    :return: wind_vector: Wind vector in new format.
    """

    if not sharppy_wind_vector[0] or not sharppy_wind_vector[1]:
        return numpy.full(2, numpy.nan)

    return numpy.asarray(sharppy_utils.vec2comp(
        sharppy_wind_vector[0], sharppy_wind_vector[1]))


def _fix_sharppy_wind_vectors(profile_object):
    """Converts a few SHARPpy wind vectors.

    This method works on a single sounding (profile_object).

    For input/output formats, see _fix_sharppy_wind_vector.

    :param profile_object: Instance of `sharppy.sharptab.Profile`.
    :return: profile_object: Same as input, except that all wind vectors are in
        the same format.
    """

    for this_sharppy_name in SHARPPY_NAMES_FOR_MASKED_WIND_ARRAYS:
        setattr(profile_object, this_sharppy_name, _fix_sharppy_wind_vector(
            getattr(profile_object, this_sharppy_name)))

    return profile_object


def _sharppy_profile_to_table(profile_object, sounding_index_metadata_table):
    """Converts SHARPpy profile to pandas DataFrame.

    This method works on a single sounding (profile_object).

    :param profile_object: Instance of `sharppy.sharptab.Profile`.
    :param sounding_index_metadata_table: pandas DataFrame created by
        read_metadata_for_sounding_indices.
    :return: sounding_index_table_sharppy: pandas DataFrame, where column names
        are SHARPpy names for sounding indices and values are in SHARPpy units.
    """

    profile_object.mupcl.brndenom = profile_object.mupcl.brnshear
    profile_object.mupcl.brnshear = numpy.array(
        [profile_object.mupcl.brnu, profile_object.mupcl.brnv])

    is_vector_flags = sounding_index_metadata_table[IS_VECTOR_COLUMN].values
    vector_rows = numpy.where(is_vector_flags)[0]
    scalar_rows = numpy.where(numpy.invert(is_vector_flags))[0]

    nan_array = numpy.array([numpy.nan])
    sounding_index_names_sharppy = sounding_index_metadata_table[
        SI_NAME_COLUMN_SHARPPY].values

    sounding_index_dict_sharppy = {}
    for this_row in scalar_rows:
        sounding_index_dict_sharppy.update(
            {sounding_index_names_sharppy[this_row]: nan_array})
    sounding_index_table_sharppy = pandas.DataFrame.from_dict(
        sounding_index_dict_sharppy)

    this_scalar_index_name = list(sounding_index_table_sharppy)[0]
    nested_array = sounding_index_table_sharppy[[
        this_scalar_index_name, this_scalar_index_name]].values.tolist()

    argument_dict = {}
    for this_row in vector_rows:
        argument_dict.update(
            {sounding_index_names_sharppy[this_row]: nested_array})
    sounding_index_table_sharppy = sounding_index_table_sharppy.assign(
        **argument_dict)

    num_sounding_indices = len(sounding_index_names_sharppy)
    for j in range(num_sounding_indices):
        if sounding_index_names_sharppy[j] in HELICITY_NAMES_SHARPPY:
            this_vector = getattr(
                profile_object, sounding_index_names_sharppy[j])
            sounding_index_table_sharppy[
                sounding_index_names_sharppy[j]].values[0] = this_vector[1]

        elif sounding_index_metadata_table[IN_MUPCL_OBJECT_COLUMN].values[j]:
            sounding_index_table_sharppy[
                sounding_index_names_sharppy[j]].values[0] = getattr(
                    profile_object.mupcl, sounding_index_names_sharppy[j])
        else:
            sounding_index_table_sharppy[
                sounding_index_names_sharppy[j]].values[0] = getattr(
                    profile_object, sounding_index_names_sharppy[j])

    return sounding_index_table_sharppy


def _split_vector_column(input_table, conversion_factor=1.):
    """Splits column of 2-D vectors into 5 columns, listed below:

    - x-component
    - y-component
    - magnitude
    - sine of direction
    - cosine of direction

    N = number of vectors

    :param input_table: pandas DataFrame with one column, where each row is a
        2-D vector.
    :param conversion_factor: Each vector component (and thus the magnitude)
        will be multiplied by this factor.
    :return: output_dict: Dictionary with the following keys (assuming that the
        original column name is "foo").
    output_dict["foo_x"]: length-N numpy array of x-components.
    output_dict["foo_y"]: length-N numpy array of y-components.
    output_dict["foo_magnitude"]: length-N numpy array of magnitudes.
    output_dict["foo_cos"]: length-N numpy array with cosines of vector
        directions.
    output_dict["foo_sin"]: length-N numpy array with sines of vector
        directions.
    """

    input_column = list(input_table)[0]
    num_vectors = len(input_table.index)
    x_components = numpy.full(num_vectors, numpy.nan)
    y_components = numpy.full(num_vectors, numpy.nan)

    for i in range(num_vectors):
        x_components[i] = input_table[input_column].values[i][0]
        y_components[i] = input_table[input_column].values[i][1]

    x_components *= conversion_factor
    y_components *= conversion_factor
    magnitudes = numpy.sqrt(x_components ** 2 + y_components ** 2)
    cosines = x_components / magnitudes
    sines = y_components / magnitudes

    return {
        '{0:s}_{1:s}'.format(input_column, X_COMPONENT_SUFFIX): x_components,
        '{0:s}_{1:s}'.format(input_column, Y_COMPONENT_SUFFIX): y_components,
        '{0:s}_{1:s}'.format(input_column, MAGNITUDE_SUFFIX): magnitudes,
        '{0:s}_{1:s}'.format(input_column, COSINE_SUFFIX): cosines,
        '{0:s}_{1:s}'.format(input_column, SINE_SUFFIX): sines}


def _convert_sounding_to_sharppy_units(sounding_table):
    """Converts sounding table from GewitterGefahr units to SHARPpy units.

    :param sounding_table: pandas DataFrame with the following columns (must
        contain either relative_humidity_percent or specific_humidity; does not
        need both).
    sounding_table.pressure_mb: Pressure (millibars).
    sounding_table.temperature_kelvins: Temperature.
    sounding_table.relative_humidity_percent: [optional] Relative humidity.
    sounding_table.specific_humidity: [optional] Specific humidity (unitless).
    sounding_table.geopotential_height_metres: Geopotential height.
    sounding_table.u_wind_m_s01: u-wind (metres per second).
    sounding_table.v_wind_m_s01: v-wind (metres per second).
    :return: sounding_table: pandas DataFrame required by
        get_sounding_indices_from_sharppy.
    """

    columns_to_drop = [nwp_model_utils.TEMPERATURE_COLUMN_FOR_SOUNDING_TABLES,
                       nwp_model_utils.U_WIND_COLUMN_FOR_SOUNDING_TABLES,
                       nwp_model_utils.V_WIND_COLUMN_FOR_SOUNDING_TABLES]

    if nwp_model_utils.SPFH_COLUMN_FOR_SOUNDING_TABLES in sounding_table:
        columns_to_drop.append(nwp_model_utils.SPFH_COLUMN_FOR_SOUNDING_TABLES)

        dewpoints_kelvins = moisture_conversions.specific_humidity_to_dewpoint(
            sounding_table[
                nwp_model_utils.SPFH_COLUMN_FOR_SOUNDING_TABLES].values,
            sounding_table[PRESSURE_COLUMN_FOR_SHARPPY].values * MB_TO_PASCALS)
    else:
        columns_to_drop.append(nwp_model_utils.RH_COLUMN_FOR_SOUNDING_TABLES)

        dewpoints_kelvins = moisture_conversions.relative_humidity_to_dewpoint(
            PERCENT_TO_UNITLESS * sounding_table[
                nwp_model_utils.RH_COLUMN_FOR_SOUNDING_TABLES].values,
            sounding_table[
                nwp_model_utils.TEMPERATURE_COLUMN_FOR_SOUNDING_TABLES].values,
            sounding_table[PRESSURE_COLUMN_FOR_SHARPPY].values * MB_TO_PASCALS)

    dewpoints_deg_c = temperature_conversions.kelvins_to_celsius(
        dewpoints_kelvins)
    temperatures_deg_c = temperature_conversions.kelvins_to_celsius(
        sounding_table[
            nwp_model_utils.TEMPERATURE_COLUMN_FOR_SOUNDING_TABLES].values)
    u_winds_kt = METRES_PER_SECOND_TO_KT * sounding_table[
        nwp_model_utils.U_WIND_COLUMN_FOR_SOUNDING_TABLES].values
    v_winds_kt = METRES_PER_SECOND_TO_KT * sounding_table[
        nwp_model_utils.V_WIND_COLUMN_FOR_SOUNDING_TABLES].values

    argument_dict = {DEWPOINT_COLUMN_FOR_SHARPPY: dewpoints_deg_c,
                     TEMPERATURE_COLUMN_FOR_SHARPPY: temperatures_deg_c,
                     U_WIND_COLUMN_FOR_SHARPPY: u_winds_kt,
                     V_WIND_COLUMN_FOR_SHARPPY: v_winds_kt}
    sounding_table = sounding_table.assign(**argument_dict)
    return sounding_table.drop(columns_to_drop, axis=1)


def read_metadata_for_sounding_indices():
    """Reads metadata for sounding indices.

    :return: sounding_index_metadata_table: pandas DataFrame with the following
        columns.
    sounding_index_metadata_table.sounding_index_name: Name of sounding index in
        GewitterGefahr format.
    sounding_index_metadata_table.sounding_index_name_sharppy: Name of sounding
        index in SHARPpy format.
    sounding_index_metadata_table.conversion_factor: Conversion factor
        (multiplier) from SHARPpy units to GewitterGefahr units.
    sounding_index_metadata_table.is_vector: Boolean flag.  If True, the
        sounding index is a 2-D vector.  If False, the sounding index is a
        scalar.
    sounding_index_metadata_table.in_mupcl_object: Boolean flag.  If True, the
        sounding index is an attribute of profile_object.mupcl, where
        profile_object is an instance of `sharppy.sharptab.Profile`.  If False,
        the sounding index is an attribute of just profile_object.
    """

    error_checking.assert_file_exists(METAFILE_NAME_FOR_SOUNDING_INDICES)
    return pandas.read_csv(
        METAFILE_NAME_FOR_SOUNDING_INDICES, header=0,
        usecols=SI_METADATA_COLUMNS, dtype=METADATA_COLUMN_TYPE_DICT)


def interp_soundings_from_nwp(query_point_table, model_name=None, grid_id=None,
                              top_grib_directory_name=None):
    """Interpolates soundings from NWP model to query points.

    Each query point consists of (latitude, longitude, time).

    :param query_point_table: pandas DataFrame in format specified by
        `interp.interp_nwp_fields_from_xy_grid`.
    :param model_name: Name of model.
    :param grid_id: String ID for model grid.
    :param top_grib_directory_name: Name of top-level directory with grib files
        for given model.
    :return: interp_table: pandas DataFrame, where each column is one field and
        each row is one query point.  Column names are given by the list
        sounding_field_names produced by `_get_nwp_fields_in_sounding`.
    """

    sounding_field_names, sounding_field_names_grib1 = (
        _get_nwp_fields_in_sounding(model_name, return_dict=False))

    return interp.interp_nwp_fields_from_xy_grid(
        query_point_table, model_name=model_name, grid_id=grid_id,
        field_names=sounding_field_names,
        field_names_grib1=sounding_field_names_grib1,
        top_grib_directory_name=top_grib_directory_name,
        temporal_interp_method=TEMPORAL_INTERP_METHOD,
        spatial_interp_method=SPATIAL_INTERP_METHOD)


def interp_table_to_sharppy_sounding_tables(interp_table, model_name):
    """Converts each row of interp table to sounding table for input to SHARPpy.

    N = number of soundings
    P = number of pressure levels in each sounding

    :param interp_table: N-row pandas DataFrame created by
        `interp.interp_nwp_fields_from_xy_grid`, where each column is one model
        field (e.g., 500-mb height or 600-mb temperature).
    :param model_name: Name of NWP model used to create interp_table.
    :return: list_of_sounding_tables: length-N list of sounding tables.  Each
        table is a pandas DataFrame in the format required by
        get_sounding_indices_from_sharppy.
    """

    # TODO(thunderhoser): Might be able to produce one output table and convert
    # units faster?

    sounding_table_to_field_dict, pressure_levels_mb = (
        _get_nwp_fields_in_sounding(model_name, return_dict=True))
    sounding_table_columns = sounding_table_to_field_dict.keys()
    num_sounding_table_columns = len(sounding_table_columns)

    lowest_pressure_name, _ = nwp_model_utils.get_lowest_pressure_name(
        model_name)

    pressure_levels_mb = numpy.concatenate((
        pressure_levels_mb, numpy.array([numpy.nan])))
    is_surface_flags = numpy.full(len(pressure_levels_mb), False, dtype=int)
    is_surface_flags[-1] = True

    base_sounding_dict = {
        PRESSURE_COLUMN_FOR_SHARPPY: pressure_levels_mb,
        IS_SURFACE_COLUMN: is_surface_flags}
    base_sounding_table = pandas.DataFrame.from_dict(base_sounding_dict)

    num_soundings = len(interp_table.index)
    list_of_sounding_tables = [base_sounding_table] * num_soundings

    for i in range(num_soundings):
        for j in range(num_sounding_table_columns):
            these_sounding_field_names = sounding_table_to_field_dict[
                sounding_table_columns[j]]

            argument_dict = {
                sounding_table_columns[j]:
                    interp_table[these_sounding_field_names].values[i]}
            list_of_sounding_tables[i] = list_of_sounding_tables[i].assign(
                **argument_dict)

        list_of_sounding_tables[i][PRESSURE_COLUMN_FOR_SHARPPY].values[
            -1] = PASCALS_TO_MB * interp_table[lowest_pressure_name].values[i]
        list_of_sounding_tables[i] = _convert_sounding_to_sharppy_units(
            list_of_sounding_tables[i])

    return list_of_sounding_tables


def get_sounding_indices_from_sharppy(sounding_table, eastward_motion_kt=None,
                                      northward_motion_kt=None,
                                      sounding_index_metadata_table=None):
    """Computes sounding indices (CAPE, CIN, shears, layer-mean winds, etc.).

    This method works on a single sounding.

    :param sounding_table: pandas DataFrame with the following columns.
    sounding_table.pressure_mb: Pressure (millibars).
    sounding_table.geopotential_height_metres: Geopotential height.
    sounding_table.temperature_deg_c: Temperature.
    sounding_table.dewpoint_deg_c: Temperature.
    sounding_table.u_wind_kt: u-wind (knots).
    sounding_table.v_wind_kt: v-wind (knots).
    sounding_table.is_surface: Boolean flag, indicating which row is the surface
        level.

    :param eastward_motion_kt: u-component of storm motion (knots).
    :param northward_motion_kt: v-component of storm motion (knots).
    :param sounding_index_metadata_table: pandas DataFrame created by
        read_metadata_for_sounding_indices.
    :return: sounding_index_table_sharppy: pandas DataFrame, where column names
        are SHARPpy names for sounding indices and values are in SHARPpy units.
    """

    error_checking.assert_is_not_nan(eastward_motion_kt)
    error_checking.assert_is_not_nan(northward_motion_kt)

    sounding_table = _remove_subsurface_sounding_data(
        sounding_table, delete_rows=False)
    sounding_table = _sort_sounding_by_height(sounding_table)
    sounding_table = _remove_redundant_sounding_data(sounding_table)

    try:
        profile_object = sharppy_profile.create_profile(
            profile='convective',
            pres=sounding_table[PRESSURE_COLUMN_FOR_SHARPPY].values,
            hght=sounding_table[HEIGHT_COLUMN_FOR_SHARPPY].values,
            tmpc=sounding_table[TEMPERATURE_COLUMN_FOR_SHARPPY].values,
            dwpc=sounding_table[DEWPOINT_COLUMN_FOR_SHARPPY].values,
            u=sounding_table[U_WIND_COLUMN_FOR_SHARPPY].values,
            v=sounding_table[V_WIND_COLUMN_FOR_SHARPPY].values)

    except:
        sounding_table = _remove_subsurface_sounding_data(
            sounding_table, delete_rows=True)

        profile_object = sharppy_profile.create_profile(
            profile='convective',
            pres=sounding_table[PRESSURE_COLUMN_FOR_SHARPPY].values,
            hght=sounding_table[HEIGHT_COLUMN_FOR_SHARPPY].values,
            tmpc=sounding_table[TEMPERATURE_COLUMN_FOR_SHARPPY].values,
            dwpc=sounding_table[DEWPOINT_COLUMN_FOR_SHARPPY].values,
            u=sounding_table[U_WIND_COLUMN_FOR_SHARPPY].values,
            v=sounding_table[V_WIND_COLUMN_FOR_SHARPPY].values)

    profile_object.right_esrh = sharppy_winds.helicity(
        profile_object, profile_object.ebotm, profile_object.etopm,
        stu=profile_object.srwind[0], stv=profile_object.srwind[1])
    profile_object.right_ehi = sharppy_params.ehi(
        profile_object, profile_object.mupcl, profile_object.ebotm,
        profile_object.etopm, stu=profile_object.srwind[0],
        stv=profile_object.srwind[1])
    profile_object.left_ehi = sharppy_params.ehi(
        profile_object, profile_object.mupcl, profile_object.ebotm,
        profile_object.etopm, stu=profile_object.srwind[2],
        stv=profile_object.srwind[3])

    profile_object.lhp = sharppy_params.lhp(profile_object)
    profile_object.x_totals = sharppy_params.c_totals(profile_object)
    profile_object.v_totals = sharppy_params.v_totals(profile_object)
    profile_object.sherb = sharppy_params.sherb(
        profile_object, effective=True, ebottom=profile_object.ebottom,
        etop=profile_object.etop, mupcl=profile_object.mupcl)
    profile_object.dcp = sharppy_params.dcp(profile_object)
    profile_object.sweat = sharppy_params.sweat(profile_object)
    profile_object.thetae_diff = sharppy_params.thetae_diff(
        profile_object)

    profile_object.right_scp = sharppy_params.scp(
        profile_object.mupcl.bplus, profile_object.right_esrh[0],
        profile_object.ebwspd * KT_TO_METRES_PER_SECOND)

    boundary_layer_top_mb = sharppy_params.pbl_top(profile_object)
    boundary_layer_top_m_asl = sharppy_interp.hght(
        profile_object, boundary_layer_top_mb)
    profile_object.pbl_depth = sharppy_interp.to_agl(
        profile_object, boundary_layer_top_m_asl)
    profile_object.edepthm = profile_object.etopm - profile_object.ebotm

    profile_object = _adjust_sounding_indices_for_storm_motion(
        profile_object, eastward_motion_kt=eastward_motion_kt,
        northward_motion_kt=northward_motion_kt)
    profile_object = _fix_sharppy_wind_vectors(profile_object)
    return _sharppy_profile_to_table(profile_object,
                                     sounding_index_metadata_table)


def convert_sounding_indices_from_sharppy(sounding_index_table_sharppy,
                                          sounding_index_metadata_table):
    """Converts names and units of sounding indices.

    :param sounding_index_table_sharppy: pandas DataFrame with columns generated
        by get_sounding_indices_from_sharppy.  Each row is one sounding.
    :param sounding_index_metadata_table: pandas DataFrame created by
        read_metadata_for_sounding_indices.
    :return: sounding_index_table: pandas DataFrame, where column names are
        GewitterGefahr names for sounding indices (including units).  Each row
        is one sounding.  Vectors are split into components, so each column is
        either a scalar sounding index or one component of a vector.
    """

    orig_column_names = list(sounding_index_table_sharppy)
    sounding_index_table = None

    for this_orig_name in orig_column_names:
        match_flags = [
            s == this_orig_name for s in sounding_index_metadata_table[
                SI_NAME_COLUMN_SHARPPY].values]
        match_index = numpy.where(match_flags)[0][0]

        this_new_name = sounding_index_metadata_table[
            SI_NAME_COLUMN].values[match_index]
        this_conversion_factor = sounding_index_metadata_table[
            CONVERSION_FACTOR_COLUMN].values[match_index]
        this_vector_flag = sounding_index_metadata_table[
            IS_VECTOR_COLUMN].values[match_index]

        if this_vector_flag:
            this_column_as_table = sounding_index_table_sharppy[[
                this_orig_name]]
            this_column_as_table.rename(
                columns={this_orig_name: this_new_name}, inplace=True)
            argument_dict = _split_vector_column(
                this_column_as_table, this_conversion_factor)
        else:
            argument_dict = {
                this_new_name:
                    this_conversion_factor * sounding_index_table_sharppy[
                        this_orig_name].values}

        if sounding_index_table is None:
            sounding_index_table = pandas.DataFrame.from_dict(argument_dict)
        else:
            sounding_index_table = sounding_index_table.assign(**argument_dict)

    temperatures_kelvins = temperature_conversions.fahrenheit_to_kelvins(
        sounding_index_table[CONVECTIVE_TEMPERATURE_NAME].values)
    argument_dict = {CONVECTIVE_TEMPERATURE_NAME: temperatures_kelvins}
    return sounding_index_table.assign(**argument_dict)


def get_sounding_indices_for_storm_objects(storm_object_table, model_name=None,
                                           grid_id=None,
                                           top_grib_directory_name=None):
    """Computes sounding indices for each storm object.

    K = number of sounding indices, after decomposition of vectors into scalars

    :param storm_object_table: pandas DataFrame with columns documented in
        `storm_tracking_io.write_processed_file`.  May contain additional
        columns.
    :param model_name: Name of NWP model from which soundings will be
        interpolated.
    :param grid_id: String ID for model grid.
    :param top_grib_directory_name: Name of top-level directory with grib files
        for the given model.
    :return: storm_object_table: Same as input, but with K additional columns.
        Names of additional columns come from column "sounding_index_name" of
        the table generated by read_metadata_for_sounding_indices.
    """

    query_point_table = storm_object_table[[
        tracking_io.CENTROID_LAT_COLUMN, tracking_io.CENTROID_LNG_COLUMN,
        tracking_io.TIME_COLUMN]]

    column_dict_old_to_new = {
        tracking_io.CENTROID_LAT_COLUMN: interp.QUERY_LAT_COLUMN,
        tracking_io.CENTROID_LNG_COLUMN: interp.QUERY_LNG_COLUMN,
        tracking_io.TIME_COLUMN: interp.QUERY_TIME_COLUMN}
    query_point_table.rename(columns=column_dict_old_to_new, inplace=True)

    interp_table = interp_soundings_from_nwp(
        query_point_table, model_name=model_name, grid_id=grid_id,
        top_grib_directory_name=top_grib_directory_name)

    list_of_sounding_tables = interp_table_to_sharppy_sounding_tables(
        interp_table, model_name)

    num_storm_objects = len(list_of_sounding_tables)
    list_of_sharppy_index_tables = [None] * num_storm_objects
    sounding_index_metadata_table = read_metadata_for_sounding_indices()

    for i in range(num_storm_objects):
        print ('Computing sounding indices for storm object ' + str(i + 1) +
               '/' + str(num_storm_objects) + '...')

        list_of_sharppy_index_tables[i] = get_sounding_indices_from_sharppy(
            list_of_sounding_tables[i],
            eastward_motion_kt=
            storm_object_table[tracking_io.EAST_VELOCITY_COLUMN].values[i],
            northward_motion_kt=
            storm_object_table[tracking_io.NORTH_VELOCITY_COLUMN].values[i],
            sounding_index_metadata_table=sounding_index_metadata_table)

        if i == 0:
            continue

        list_of_sharppy_index_tables[i], _ = (
            list_of_sharppy_index_tables[i].align(
                list_of_sharppy_index_tables[0], axis=1))

    sounding_index_table_sharppy = pandas.concat(
        list_of_sharppy_index_tables, axis=0, ignore_index=True)
    sounding_index_table = convert_sounding_indices_from_sharppy(
        sounding_index_table_sharppy, sounding_index_metadata_table)
    return pandas.concat([storm_object_table, sounding_index_table], axis=1)
