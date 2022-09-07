"""!
\file phantom.py

\brief Methods to do the generation of the phantom
"""

from operator import mod
import os
import numpy as np
import matplotlib.pyplot
import math
import scipy.io
from . import structures as struc
import utils as ut
from PIL import Image
import pydicom as dicom


class Phantom():
    """!
    \brief The 2-D phantom. 3-D phantoms are built with one 2-D phantom per slice
    """

    def generate_phantom_from_image(self, config):
        """!
        \brief Generates the scatterers of a phantom created from an image

        \param config The parsed configuration
        """

        ## Statistical distribution of the scatterers in the phantom
        self.dist = config["distribution"].lower()

        ## Percentage of scatterers in the phantom
        self.dens = config["perc_of_scatterers"]

        # Load gray-scale image and get x_cols and rows_y
        input_image = config["image_path"]

        ## 2-D array that will store the scatterers amplitude
        if input_image.lower().endswith('.dcm'):
            self.phantom = dicom.dcmread(input_image).pixel_array
            self.phantom = np.transpose(self.phantom.astype(complex))
        else:
            self.phantom = np.transpose(np.array(Image.open(input_image).convert('L'), dtype=np.complex_))

        ## Number of rows in the phantom
        self.num_of_rows = self.phantom.shape[1]

        ## Number of columns in the phantom
        self.num_of_cols = self.phantom.shape[0]

        ## Format of phantom (e.g. k-Wave compatible)
        self.phantom_format = config["phantom_format"].lower()

        ## Sound speed in the tissue 1540 m/s
        self.c0 = config.get("sound_speed_c0_m_per_s", 1540)  # [m/s]

        ## Density of the tissue - set to 1000 kg/m^3
        self.rho0 = config.get("density_rho0_kg_per_m3", 1000)  # [kg/m^3]

        ## 2-D array that will store the sound speed values (only for k-Wave format)
        self.sound_speed_map = [[self.c0 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]

        ## 2-D array that will store the density values (only for k-Wave format)
        self.density_map = [[self.rho0 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]

        self.generate_scatterers(config)

    def generate_phantom_matrix(self, config, slice_z = 0):
        """!
        \brief Generates a 2-D phantom (structures + scatterers)

        \param config The parsed configuration
        \param slice_z Current slice of a 3-D phantom or 0 for a 2-D phantom

        \note Raises an exception if no known structure is specified
        """

        # Use config.distribution and config.perc_of_scatterers to generate a phantom with the desired distribution
        # Iterate through structures and fill the desired areas

        self.dist = config["distribution"].lower()
        self.dens = config["perc_of_scatterers"]
        self.num_of_rows = config["rows_y"]
        self.num_of_cols = config["cols_x"]
        self.phantom = np.zeros((self.num_of_cols, self.num_of_rows), dtype=np.complex_)

        self.phantom_format = config["phantom_format"].lower()

        self.c0 = config.get("sound_speed_c0_m_per_s", 1540)   # [m/s]
        self.rho0 = config.get("density_rho0_kg_per_m3", 1000) # [kg/m^3]

        self.sound_speed_map = [[self.c0 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]
        self.density_map = [[self.rho0 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]

        self.generate_scatterers(config)

        for region in config["structures"]:
            region_type = region["type"].lower()
            ut.log_message("Adding " + region_type)
            if region_type == "circle":
                circ = struc.Circle([struc.Point(region["center_xy"])], region["radius"])
                circ.fill_area(self.phantom, self.sound_speed_map, self.density_map, region["scat_gain"], config)
            elif region_type == "sphere":
                sphere = struc.Sphere([struc.Point(region["center_xyz"])], region["radius"])
                sphere.fill_volume(self.phantom, slice_z, self.sound_speed_map, self.density_map, region["scat_gain"], config)
            elif region_type == "rectangle":
                rec = struc.Rectangle([struc.Point((region["top_left_corner_xy"]))], region["length_x"], region["length_y"])
                rec.fill_area(self.phantom, self.sound_speed_map, self.density_map, region["scat_gain"], config)
            elif region_type == "free_polygon":
                polygon = []
                for point in range(len(region["vertices_xy"])):
                    polygon.append(struc.Point(region["vertices_xy"][point]))

                poly = struc.Polygon(polygon)
                poly.fill_area(self.phantom, self.sound_speed_map, self.density_map, region["scat_gain"], config)
            elif region_type == "points":
                points = []
                for point in range(len(region["coordinates_xy"])):
                    points.append(struc.Point(region["coordinates_xy"][point]))

                s_points = struc.SinglePoint(points)
                s_points.fill_area(self.phantom, self.sound_speed_map, self.density_map, region["scat_gain"], config)
            else:
                raise Exception("Unknown structure defined: " + region_type)

    def generate_scatterers(self, config):
        """!
        \brief Generates the scatterers added to the phantom

        \param config The parsed configuration

        \note Raises an exception if no known distribution is specified
        """

        k = round((self.dens/100)*self.num_of_rows*self.num_of_cols) # Absolute number of scatterers

        ut.log_message("Using distribution " + self.dist)

        x = np.random.uniform(size=(k))
        y = np.random.uniform(size=(k))

        if self.dist == "uniform":
            amp = np.random.uniform(size=(k))
            phase = 2*math.pi*np.random.uniform(size=(k))
        elif self.dist == "gaussian":
            amp = np.random.normal(loc=1, scale=0.008, size=(k))
            phase = 2*math.pi*np.random.normal(loc=1, scale=0.008, size=(k))
        elif self.dist == "rayleigh":
            amp = np.random.rayleigh(scale=2, size=(k))
            phase = 2*math.pi*np.random.rayleigh(scale=2, size=(k))
        else:
            raise Exception("Unknown distribution defined: " + self.dist)

        x = x - np.amin(x)
        max_x = np.amax(abs(x))
        x = x/max_x
        max_x = np.amax(abs(x))
        x = (np.around((self.num_of_cols - 1)*(x/max_x))).astype(int)

        y = y - np.amin(y)
        max_y = np.amax(abs(y))
        y = y/max_y
        max_y = np.amax(abs(y))
        y = (np.around((self.num_of_rows - 1)*(y/max_y))).astype(int)

        # Complex random scatterers
        scatterers = [0 for i in range(k)]

        for i in range(k):
            if mod(i, 10000) == 0:
                ut.log_message("Generating scatterer " + str(i) + "/" + str(k), config.get("verbose", False))

            scatterers[i] = complex(amp[i]*math.cos(phase[i]), amp[i]*math.sin(phase[i]))  # Complex scatterers (real and imaginary part)

        # Distribution of the scatterers along the image
        for i in range(k):
            if mod(i, 10000) == 0:
                ut.log_message("Storing scatterer " + str(i) + "/" + str(k), config.get("verbose", False))

            self.phantom[x[i]][y[i]] = scatterers[i]

    def save_all(self, output_format, full_path):
        """!
        \brief Saves the phantom in all possible formats

        \param output_format Format to save the phantom ('t' - txt, 'm' - mat or 'p' - png)
        \param full_path Full path (folder + filename) without extension
        """

        if 't' in output_format:
            self.save_txt_file(full_path)
        if 'm' in output_format:
            self.save_mat_file(full_path)
        if 'p' in output_format:
            self.save_png_image(full_path)

    def save_txt_file(self, output_path_name):
        """!
        \brief Saves the phantom in a text file

        \param output_path_name Full path (folder + filename) without extension
        """

        full_path = os.path.join(output_path_name + ".txt")
        ut.log_message("Saving text file to to " + full_path)
        np.savetxt(full_path, self.phantom)

    def create_mat_file(self, data):
        """!
        \brief Saves data in a mat file. Array name is fixed as 'arr'

        \param data Data to be stored in the mat file
        """

        temp = np.array(data)
        temp = np.transpose(temp)
        scipy.io.savemat(self.full_path, mdict={'arr': temp})

    def save_mat_file(self, output_path_name):
        """!
        \brief Saves the 2-D phantom in a mat file. Extra outputs are saved for k-Wave phantom

        \param output_path_name Full path (folder + filename) without extension
        """

        ## The path + complete filename of the mat file that will be created
        self.full_path = os.path.join(output_path_name + ".mat")
        ut.log_message("Saving phantom as mat file to " + self.full_path)
        self.create_mat_file(self.phantom)

        if self.phantom_format == "k_wave":
            self.full_path = os.path.join(output_path_name + "_sound_speed_map.mat")
            ut.log_message("Saving phantom sound speed map as mat file to " + self.full_path)
            self.create_mat_file(self.sound_speed_map)

            self.full_path = os.path.join(output_path_name + "_density_map.mat")
            ut.log_message("Saving phantom density map as mat file to " + self.full_path)
            self.create_mat_file(self.density_map)

    def create_png_image(self, data):
        """!
        \brief Creates the png file on disk

        \param data Data to be stored in the png file
        """

        temp = np.transpose(data)
        temp = abs(temp)
        min_t = np.amin(temp)
        temp = temp - min_t
        data_max = np.amax(temp)
        normalized = temp*255/data_max
        normalized = normalized.astype(np.uint8)

        matplotlib.pyplot.imsave(self.full_path, normalized, cmap='gray')

    def save_png_image(self, output_path_name):
        """!
        \brief Saves the 2-D phantom in a png file. Extra outputs are saved for k-Wave phantom

        \param output_path_name Full path (folder + filename) without extension
        """

        self.full_path = os.path.join(output_path_name + ".png")
        ut.log_message("Saving phantom image to " + self.full_path)
        temp = np.array(self.phantom)
        self.create_png_image(temp)

        if self.phantom_format == "k_wave":
            self.full_path = os.path.join(output_path_name + "_density_map.png")
            ut.log_message("Saving phantom density map as image to " + self.full_path)
            temp = np.array(self.density_map)
            self.create_png_image(temp)

            self.full_path = os.path.join(output_path_name + "_sound_speed_map.png")
            ut.log_message("Saving phantom sound map as image to " + self.full_path)
            temp = np.array(self.sound_speed_map)
            self.create_png_image(temp)

    def generate_final_output(self, configuration, name_path_prefix):
        """!
        \brief Generates a final mat file when multiples mat files are created during processing

        \param configuration Parsed configuration
        \param name_path_prefix Path + filename prefix
        """

        num_of_z = configuration.get("depth_z", 1)
        if num_of_z == 1:
            # There is no file to append
            return

        phantom_format = configuration["phantom_format"].lower()

        ## Set to True if the message should be logged
        self.verbose = configuration["verbose"]

        if phantom_format == "k_wave":
            # Split in three loops to save memory
            ut.log_message("Creating final 3-D phantom " + name_path_prefix + ".mat")
            self.mat_2d_to_3d(name_path_prefix, "", num_of_z, "phantom")

            ut.log_message("Creating 3-D sound speed map " + name_path_prefix + "_sound_speed_map.mat")
            self.mat_2d_to_3d(name_path_prefix, "_sound_speed_map", num_of_z, "sound_speed_map")

            ut.log_message("Creating 3-D density map " + name_path_prefix + "_density_map.mat")
            self.mat_2d_to_3d(name_path_prefix, "_density_map", num_of_z, "density_map")

    def mat_2d_to_3d(self, name_path_prefix, postfix, num_of_slices, array_name):
        """!
        \brief Loads a series of 2-D mat files and generate a final 3-D file

        \param name_path_prefix Path + filename prefix
        \param postfix String to append to the filename
        \param num_of_slices Total number of slices in the 3-D phantom
        \param array_name Name to used internally in the .mat file
        """

        data = scipy.io.loadmat(name_path_prefix + "_slice_0" + postfix + ".mat")
        mx = data['arr']  # Matrix MxN
        volume = mx[..., np.newaxis]  # Volume MxNx1

        for slice_z in range(1, num_of_slices):
            ut.log_message("Appending slice " + str(slice_z), self.verbose)
            data = scipy.io.loadmat(name_path_prefix + "_slice_" + str(slice_z) + postfix + ".mat")
            mx = data['arr']
            volume = np.dstack((volume, mx[..., np.newaxis]))

        scipy.io.savemat(name_path_prefix + postfix + ".mat", mdict={array_name:volume})
