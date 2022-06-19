"""!
\file generate_phantom.py

\brief Entry point of the application, will parse the configuration and generate the phantom
"""

import argparse
import json
import os
import sys

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import mx_us_phantom.config_validation as cfg_val
import mx_us_phantom.phantom as ph
import utils as ut


def get_example_text():
    """!
    \brief Defines the example string

    \return The example text
    """

    example_text = '''Example:

    python generate_phantom.py -c ./structures.json -o phantom_1 -f mp

    Example of json configuration file:

    {
        "rows_y":512,
        "cols_x":512,
        "distribution":"uniform",
        "perc_of_scatterers":80,
        "phantom_format":"k_wave",
        "structures": [
            { "type":"circle", "center_xy":[ 300, 300 ], "radius":50, "scat_gain":3 },
            { "type":"rectangle", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 },
            { "type":"free_polygon", "vertices_xy":[ [100, 100], [200, 100], [200, 200] ], "scat_gain":0 },
            { "type":"points", "coordinates_xy":[ [80, 90], [85, 85] ], "scat_gain":2 }
        ]
    }

    Alternatively, an image can be used as input, but only for effective scatterers format. Example:

    {
    "distribution":"rayleigh",
    "perc_of_scatterers":60,
    "phantom_format":"effec_scatterers",
    "image_path":"../input_image.bmp"
    } 

    '''

    return example_text


def parse_arguments():
    """!
    \brief Parses and check command line arguments

    \return The parsed arguments
    """

    example_text = get_example_text()

    description_text = 'Generate a matrix with random scatterers to be used as an ultrasound phantom'
    parser = argparse.ArgumentParser(description=description_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    required_named = parser.add_argument_group('Required named arguments')
    required_named.add_argument('-c', '--config', help="Specify the input json configuration file. Use forward slashes to specify a path. Example: ../config.json", required=True)
    format_help = "Define in which format the phantom will be saved. Any combination of the following three options are possible: t - save in a text file; m - save in a .mat file; p - save a png image"
    required_named.add_argument('-f', '--format', help=format_help, required=True)
    optional_args = parser.add_argument_group('Optional arguments')
    optional_args.add_argument('-o', '--output_name', help="Name of the output files (txt, mat and png). The files will be saved in the same directory where the configuration file is located. The configuration file name is used if the output name is not informed", required=False)
    optional_args.add_argument('-v', '--verbosity', help="Enables verbose output. Values: 'on' and 'off' (without quotes)", required=False)

    args = parser.parse_args()

    if 't' not in args.format and 'm' not in args.format and 'p' not in args.format:
        print("Unsupported output format defined.\r\n")
        parser.print_help()
        sys.exit(0)

    return args


def get_output_name(args):
    """!
    \brief Sets the name of the generated phantom

    \param args The parsed arguments

    \return The name used to save files
    """

    if not args.output_name:
        output_name = os.path.basename(args.config).split('.json')[0]
    else:
        output_name = args.output_name

    return output_name


def parse_config(args):
    """!
    \brief Parses the json configuration

    \note Raises an exception if an error is found

    \param args The parsed arguments

    \return The configuration parsed from the input file
    """

    with open(args.config) as json_file:
        configuration = json.load(json_file)

    # Parse verbosity and add to configuration
    if  not args.verbosity:
        verbose = False
    else:
        if args.verbosity.lower() == 'on':
            verbose = True
        else:
            verbose = False

    verbosity = {"verbose": verbose}
    configuration.update(verbosity)

    print(configuration)

    validation_error = cfg_val.validate_configuration(configuration)
    if validation_error:
        raise Exception(validation_error)

    return configuration


def gen_phantom(configuration, args, name_path_prefix):
    """!
    \brief Generates the requested phantom

    \param configuration The parsed input configuration
    \param args The parsed arguments
    \param name_path_prefix Path + prefix of the output file name
    """

    num_of_z = configuration.get("depth_z", 1)

    verbose = configuration.get("verbose", False)

    if configuration.get("image_path", "") == "":
        for slice_z in range(num_of_z):
            if (num_of_z == 1):
                postfix = ""
            else:
                postfix = "_slice_" + str(slice_z)

            ut.log_message("Generating slice " + str(slice_z), verbose)
            phantom = ph.Phantom()
            phantom.generate_phantom_matrix(configuration, slice_z)

            phantom.save_all(args.format, name_path_prefix + postfix)

        ut.log_message("Generating final output file")
        phantom.generate_final_output(configuration, name_path_prefix)
    else:
        phantom = ph.Phantom()
        phantom.generate_phantom_from_image(configuration)
        phantom.save_all(args.format, name_path_prefix)


def show_phantom(configuration, args, name_path_prefix):
    """!
    \brief Displays the generated phantom (2-D phantoms only)

    \param configuration The parsed input configuration
    \param args The parsed arguments
    \param name_path_prefix Path + prefix of the output file name
    """

    phantom_format = configuration["phantom_format"].lower()

    if phantom_format == "k_wave" and 'm' in args.format:
        plot_cmd = 'python plot_3d_phantom.py -a phantom -f ' + name_path_prefix + ".mat" + ' -m light'
        ut.log_message("You can now visualize the phantom by running \'" + plot_cmd + "\'")
    elif phantom_format == "effec_scatterers" and 'p' in args.format:
        img = mpimg.imread(name_path_prefix + ".png")
        plt.imshow(img)
        plt.title(name_path_prefix + ".png")
        plt.show()


def main():
    """!
    \brief Has the sequence of actions to generate the phantom
    """

    ut.log_message("Starting application")

    args = parse_arguments()

    output_name = get_output_name(args)

    ut.log_message("Output name: " + output_name)

    ut.log_message("Parsing configuration from " + args.config)

    configuration = parse_config(args)

    output_path = os.path.dirname(args.config)
    name_path_prefix = os.path.normpath(os.path.join(output_path, output_name))

    ut.log_message("Generating phantom \"" + output_name + "\"")

    gen_phantom(configuration, args, name_path_prefix)

    show_phantom(configuration, args, name_path_prefix)

    ut.log_message("End of execution")


if __name__ == "__main__":
    main()
