"""!
\file generate_phantom.py

\brief Entry point of the application, will parse the configuration and generate the phantom
"""

import argparse
import sys

import phantom_wrapper as phw
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
    required_named.add_argument('-o', '--output_name', help="Name of the output files (txt, mat and png). If a directory is used as input, this will be the subdirectory name", required=True)
    optional_args = parser.add_argument_group('Optional arguments')
    optional_args.add_argument('-v', '--verbosity', help="Enables verbose output. Values: 'on' and 'off' (without quotes)", required=False)

    args = parser.parse_args()

    if 't' not in args.format and 'm' not in args.format and 'p' not in args.format:
        print("Unsupported output format defined.\r\n")
        parser.print_help()
        sys.exit(0)

    return args


def main():
    """!
    \brief Has the sequence of actions to generate the phantom
    """

    ut.log_message("Starting application")

    args = parse_arguments()

    phantom = phw.PhantomWrapper(args)
    phantom.gen_phantom()
    phantom.show_phantom()

    ut.log_message("End of execution")


if __name__ == "__main__":
    main()
