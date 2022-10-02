"""!
\file config_validation.py

\brief Validate that the required parameters are present in the configuration file
"""

import warnings
from . import structures as struc
from pathlib import Path


def check_parameters_are_present(configuration, is_image):
    """!
    \brief Checks if global parameters are present

    \param configuration Parsed configuration
    \param is_image Set to True if the input for phantom generation is an image file

    \note Raises an exception if there is any error
    """

    error_msg = ""

    if not is_image:
        # Get size information from input image
        if "rows_y" not in configuration:
            error_msg = error_msg + "Parameter \"rows_y\" is missing.\r\n"

        if "cols_x" not in configuration:
            error_msg = error_msg + "Parameter \"cols_x\" is missing.\r\n"

    if "distribution" not in configuration:
        error_msg = error_msg + "Parameter \"distribution\" is missing.\r\n"

    if "perc_of_scatterers" not in configuration:
        error_msg = error_msg + "Parameter \"perc_of_scatterers\" is missing.\r\n"

    if "phantom_format" not in configuration:
        error_msg = error_msg + "Parameter \"phantom_format\" is missing.\r\n"
    else:
        if configuration["phantom_format"] == "k_wave":
            if "sound_speed_c0_m_per_s" not in configuration:
                error_msg = error_msg + "Parameter \"sound_speed_c0_m_per_s\" is missing.\r\n"
            if "density_rho0_kg_per_m3" not in configuration:
                error_msg = error_msg + "Parameter \"density_rho0_kg_per_m3\" is missing.\r\n"

    if error_msg:
        raise Exception("One of more parameters is missing in the configuration file.\r\n" + error_msg)


def validate_distribution(distribution):
    """!
    \brief Checks if a valid statiscal distribution was specified

    \param distribution String containing the desired statistical distribution

    \return An empty string if no error is found; an error string otherwise
    """

    error_msg = ""

    supported_distributions = ["uniform", "gaussian", "rayleigh"]

    if distribution not in supported_distributions:
        error_msg = 'The distribution ' + distribution + " is not supported.\r\n"
        error_msg = error_msg + "Supported distributions are:"
        for dist in supported_distributions:
            error_msg = error_msg + " " + dist

        error_msg = error_msg + ".\r\n"

    return error_msg


def validate_perc_of_scat(perc_of_scatterers):
    """!
    \brief Checks if percentage of scatterers points in the matrix is valid

    \param perc_of_scatterers Percentage of area that will be filled with scaterrers [0%, 100%]

    \return An empty string if no error is found; an error string otherwise
    """

    error_msg = ""

    if perc_of_scatterers <= 0 or perc_of_scatterers > 100:
        error_msg = error_msg + "Percentage of scatterers should be > 0 and < 100 %\r\n"
    elif perc_of_scatterers == 100:
        warnings.warn_explicit("Percentage of scatterers is set to 100 %. Please check your configuration.\r\n", UserWarning, "", 0)

    return error_msg


def validate_scat_gain(structure_type, scat_gain):
    """!
    \brief Checks if the relative amplitude of the scatterers of a region is valid

    \param structure_type The structure for which the gain is being validated
    \param scat_gain The gain of the scatterers inside the structure

    \return An empty string if no error is found; an error string otherwise
    """

    error_msg = ""

    if scat_gain < 0:
        error_msg = error_msg + "Structure " + structure_type + ": relative amplitude of the scatterers should be >= 0\r\n"

    return error_msg


def validate_phantom_format(phantom_format):
    """!
    \brief Checks if the phantom compatibility format is valid

    \param phantom_format The string with the phantom format (compatible toolbox)

    \return An empty string if no error is found; an error string otherwise
    """

    error_msg = ""

    supported_formats = ["effec_scatterers", "k_wave"]

    if phantom_format not in supported_formats:
        error_msg = 'The format ' + phantom_format + " is not supported.\r\n"
        error_msg = error_msg + "Supported formats are:"
        for dist in supported_formats:
            error_msg = error_msg + " " + dist

        error_msg = error_msg + ".\r\n"

    return error_msg


def validate_structures(structures, num_of_rows, num_of_cols, num_of_z):
    """!
    \brief Checks if the structures are valid (are within boundaries and
    contain all parameters)

    \param structures All the structures present in the configuration file
    \param num_of_rows Number of rows of the phantom
    \param num_of_cols Number of collumns of the phantom
    \param num_of_z Number of slices of the phantom (3-D phantoms)

    \return An empty string if no error is found; an error string otherwise
    """

    error_msg = ""

    supported_structures = ["circle", "rectangle", "free_polygon", "points", "sphere"]

    for region in structures:
        region_type = region["type"].lower()
        if region_type not in supported_structures:
            error_msg = 'The structure of type ' + region_type + " is not supported.\r\n"
            error_msg = error_msg + "Supported structures are:"
            for structure in supported_structures:
                error_msg = error_msg + " " + structure
        else:
            error_msg = error_msg + validate_scat_gain(region["type"], region["scat_gain"])
            if region_type == "circle":
                circ = struc.Circle([struc.Point(region["center_xy"])], region["radius"])
                error_msg = error_msg + circ.validate(num_of_rows, num_of_cols)
            elif region_type == "rectangle":
                rec = struc.Rectangle([struc.Point((region["top_left_corner_xy"]))], region["length_x"], region["length_y"])
                error_msg = error_msg + rec.validate(num_of_rows, num_of_cols)
            elif region_type == "free_polygon":
                polygon = []
                for point in range(len(region["vertices_xy"])):
                    polygon.append(struc.Point(region["vertices_xy"][point]))

                poly = struc.Polygon(polygon)
                error_msg = error_msg + poly.validate(num_of_rows, num_of_cols)
            elif region_type == "points":
                points = []
                for point in range(len(region["coordinates_xy"])):
                    points.append(struc.Point(region["coordinates_xy"][point]))

                s_points = struc.SinglePoint(points)
                error_msg = error_msg + s_points.validate(num_of_rows, num_of_cols)
            elif region_type == "sphere":
                sp = struc.Sphere([struc.Point(region["center_xyz"])], region["radius"])
                error_msg = error_msg + sp.validate(num_of_rows, num_of_cols, num_of_z)

    return error_msg


def validate_configuration(configuration):
    """!
    \brief Checks if the phantom parameters are valid

    \note Raises an exception if there is any error

    \param configuration The parsed configuration

    \return An empty string if no error is found; an error string otherwise
    """

    error_msg = ""

    image_path = configuration.get("image_path", "")

    if image_path == "":
        check_parameters_are_present(configuration, False)
    else:
        check_parameters_are_present(configuration, True)

    # Statiscal distributions used to generate the scatterers
    error_msg = error_msg + validate_distribution(configuration["distribution"].lower())

    # Percentage of scatterers (non-zero elements) in the final matrix
    perc_of_scatterers = configuration["perc_of_scatterers"]
    error_msg = error_msg + validate_perc_of_scat(perc_of_scatterers)

    # Phantom format
    phantom_format = configuration["phantom_format"].lower()
    error_msg = error_msg + validate_phantom_format(phantom_format)

    if image_path == "":
        # Matrix size
        rows = configuration["rows_y"]
        cols = configuration["cols_x"]
        num_of_z = configuration.get("depth_z", 1)
        if (num_of_z > 1) and (phantom_format == "effec_scatterers"):
            error_msg = error_msg + "effec_scatterers only supports 2-D phantoms\r\n"

        # Check if the structures defined are valid
        error_msg = error_msg + validate_structures(configuration["structures"], rows, cols, num_of_z)
    else:
        input_image = Path(image_path)

        if not input_image.is_file() and not input_image.is_dir():
            raise Exception("Input image \"" + image_path + "\" was not found.")

        if (phantom_format != "effec_scatterers"):
            error_msg = error_msg + "Using image as input is supported only with effec_scatterers format\r\n"

    return error_msg
