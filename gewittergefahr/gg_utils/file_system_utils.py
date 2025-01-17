"""Methods for file-system access."""

import os
import os.path
from gewittergefahr.gg_utils import error_checking


def mkdir_recursive_if_necessary(directory_name=None, file_name=None):
    """Creates directory if necessary (i.e., doesn't already exist).

    This method checks for the argument `directory_name` first.  If
    `directory_name` is None, this method checks for `file_name` and extracts
    the directory.

    :param directory_name: Path to local directory.
    :param file_name: Path to local file.
    """

    if directory_name is None:
        error_checking.assert_is_string(file_name)
        directory_name = os.path.dirname(file_name)
    else:
        error_checking.assert_is_string(directory_name)

    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)
