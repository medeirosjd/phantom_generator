"""!
\file phantom_wrapper.py

\brief Wrapper for the high level phantom operations
"""

import os
import json

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import mx_us_phantom.phantom as ph
import mx_us_phantom.config_validation as cfg_val
import utils as ut


class PhantomWrapper():
    """!
    \brief Set of wrappers to generate the phantoms
    """

    def __init__(self, args):
        """
        \brief Initializes the class

        \param configuration The parsed input configuration
        \param args The parsed command-line arguments
        \param output_path_prefix Path + prefix of the output in case a single
        phantom is generated or path of the directory if the input is a directory
        """
        self.args = args

        ut.log_message("Parsing configuration from " + args.config)

        self.configuration = self.parse_config()

        output_name = self.get_output_name()
        ut.log_message("Output name: " + output_name)
        output_path = os.path.dirname(args.config)
        self.output_path_prefix = os.path.normpath(os.path.join(output_path, output_name))

        ut.log_message("Generating phantom \"" + output_name + "\"")


    def get_output_name(self):
        """!
        \brief Sets the name of the generated phantom

        \return The name used to save files
        """

        if not self.args.output_name:
            output_name = os.path.basename(self.args.config).split('.json')[0]
        else:
            output_name = self.args.output_name

        return output_name


    def parse_config(self):
        """!
        \brief Parses the json configuration

        \note Raises an exception if an error is found

        \return The configuration parsed from the input file
        """

        with open(self.args.config) as json_file:
            configuration = json.load(json_file)

        # Parse verbosity and add to configuration
        if  not self.args.verbosity:
            verbose = False
        else:
            if self.args.verbosity.lower() == 'on':
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


    def gen_phantom(self):
        """!
        \brief Generates the requested phantom
        """

        if self.configuration.get("image_path", "") == "":
            self.gen_structures_phantom()
            return

        if not self.is_input_a_directory():
            self.image_path = self.configuration["image_path"]
            self.gen_image_based_phantom(self.output_path_prefix, self.image_path)
        else:
            self.gen_phantoms_from_directory()


    def is_input_a_directory(self):
        """!
        \brief Checks if the configured image input is a directory

        \return True if the input is a directory where image inputs would be located; False otherwise
        """

        if self.configuration.get("image_path", "") != "":
            input = self.configuration["image_path"]
            if os.path.isdir(input):
                return True

        return False


    def gen_structures_phantom(self):
        """!
        \brief High level wrapper to generate a phantom that have its
            structures defined in the configuration file
        """

        num_of_z = self.configuration.get("depth_z", 1)

        verbose = self.configuration.get("verbose", False)

        for slice_z in range(num_of_z):
            if (num_of_z == 1):
                postfix = ""
            else:
                postfix = "_slice_" + str(slice_z)

            ut.log_message("Generating slice " + str(slice_z), verbose)
            phantom = ph.Phantom()
            phantom.generate_phantom_matrix(self.configuration, slice_z)

            phantom.save_all(self.args.format, self.output_path_prefix + postfix)

        ut.log_message("Generating final output file")
        phantom.generate_final_output(self.configuration, self.output_path_prefix)


    def gen_image_based_phantom(self, name_path_prefix, input_image):
        """!
        \brief High level wrapper to generate a phantom from an input image

        \param name_path_prefix Path + prefix of the output file name
        \param input_image The image file used as reference to generate the phantom
        """

        phantom = ph.Phantom()
        phantom.generate_phantom_from_image(self.configuration, input_image)
        phantom.save_all(self.args.format, name_path_prefix)


    def gen_phantoms_from_directory(self):
        """!
        \brief Wrapper to generate phantoms from all input images present in a directory
        """

        if not os.path.exists(self.output_path_prefix):
            os.makedirs(self.output_path_prefix)

        for entry in os.scandir(self.configuration["image_path"]):
            if os.path.isfile(entry.path):
                try:
                    output = os.path.normpath(os.path.join(self.output_path_prefix, os.path.basename(entry.path.rsplit('.', 1)[0])))
                    self.gen_image_based_phantom(output, entry.path)
                except Exception as e:
                    print(e)


    def show_phantom(self):
        """!
        \brief Displays the generated phantom (2-D phantoms only)
        """

        # If input is a directory containing images, showing several pop-ups with
        # the output phantoms becomes inconvenient for the user
        if self.is_input_a_directory():
            return

        phantom_format = self.configuration["phantom_format"].lower()

        if phantom_format == "k_wave" and 'm' in self.args.format:
            plot_cmd = 'python plot_3d_phantom.py -a phantom -f ' + self.output_path_prefix + ".mat" + ' -m light'
            ut.log_message("You can now visualize the phantom by running \'" + plot_cmd + "\'")
        elif phantom_format == "effec_scatterers" and 'p' in self.args.format:
            img = mpimg.imread(self.output_path_prefix + ".png")
            plt.imshow(img)
            plt.title(self.output_path_prefix + ".png")
            plt.show()
