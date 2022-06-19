"""!
\file plot_3d_phantom.py

\brief Displays the 3-D phantom and save an svg with a 2-D view
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pyvista as pv
import scipy.io

import utils as ut


def get_example_text():
    """!
    \brief Defines the example string

    \return The example text
    """

    example_text = """Example:
    python plot_3d_phantom.py -a phantom -f ./examples/example_3d.mat -m light
    """
    return example_text


def parse_arguments():
    """!
    \brief Parses and check command line arguments

    \return The parsed arguments
    """

    example_text = get_example_text()

    description_text = 'Plot the 3-D phantom from the .mat file generated with generate phantom utility. An svg file named with array name and the timestamp is also generated'
    parser = argparse.ArgumentParser(description=description_text, epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    required_named = parser.add_argument_group('Required named arguments')
    required_named.add_argument('-a', '--array_name', help="The internal array name stored in the .mat file", required=True)
    required_named.add_argument('-f', '--file_name', help='Path of the 3-D mat file containing the phantom data', required=True)
    optional_args = parser.add_argument_group('Optional arguments')
    optional_args.add_argument('-m', '--color_mode', help="Options are 'light' and 'dark', without quotes", required=False)

    return parser.parse_args()


def plot_and_save(args):
    """!
    \brief Plots the 3-D data and save a 2-D view as svg file

    \param args The parsed arguments
    """

    if not args.color_mode:
        color_mode = 'light'
    else:
        color_mode = args.color_mode.lower()

    array_name = args.array_name

    data = scipy.io.loadmat(args.file_name)
    volume = data[array_name].transpose(1, 0, 2)
    max_value = np.max(np.max(np.max(np.abs(volume))))
    data_v = pv.wrap(255*np.abs(volume)/max_value) # The data is of complex type, so needs the abs()

    pl = pv.Plotter()
    if color_mode == 'dark':
        pl.show_bounds(location='outer', color=[1, 1, 1])
        pl.set_background(color=[0, 0, 0])
    else:
        pl.show_bounds(location='outer', color=[0, 0, 0])
        pl.set_background(color=[1, 1, 1])

    pl.add_volume(data_v, cmap='viridis')
    pl.add_bounding_box()
    image_name = array_name + "_" + ut.current_time_for_filename() + ".svg"
    pl.save_graphic(image_name)
    print("Saved screenshot to " + image_name)
    pl.show()


def main():
    """!
    \brief The main entry point
    """

    args = parse_arguments()

    file_name = args.file_name

    input_file = Path(file_name)

    if not input_file.exists():
        print("File \"" + file_name + "\" not found. Exiting")
        sys.exit(-1)

    plot_and_save(args)

if __name__ == "__main__":
    main()
