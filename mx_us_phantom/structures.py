"""!
\file structures.py

\brief Contains the definitions of the structures that are added to a phantom
"""

from numpy import mod
import utils as ut


# https://github.com/JoJocoder/PNPOLY/blob/master/pnpoly.py
# Originally from https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
class Point():
    """!
    \brief Class used as reference for Polygons
    """

    def __init__(self, p):
        """!
        \brief Initializes the center point of the structure

        \param p Array with the point coordinates
        """

        ## X coordinate
        self.x = p[0]

        ## Y coordinate
        self.y = p[1]

        if len(p) == 3:
            ## Z coordinate, 3-D structures only
            self.z = p[2]

    def __str__(self):
        """!
        \brief Prints the position of the center of the structure (only 2-D structures)

        \return A string with the center information
        """
        return "(x, y) = (" + str(self.x) + ", " + str(self.y) + ")"

    def in_polygon(self, polygon):
        """!
        \brief Checks if a point is inside a polygon

        \param polygon Set of points defining a polygon

        \return True if the point is inside the polygon; False otherwise
        """

        is_inside = False

        j = len(polygon) - 1
        for i in range(len(polygon)):
            if ((polygon[i].y > self.y) != (polygon[j].y > self.y) and \
                (self.x < (polygon[j].x - polygon[i].x)*(self.y - polygon[i].y)/(polygon[j].y - polygon[i].y) + polygon[i].x)):
                is_inside = not is_inside
            j = i

        return is_inside


class Structure():
    """!
    \brief Base class for 2-D structures
    """

    def __init__(self, origins, *args):
        """!
        \brief Sets the structure origin

        \param origins A set of points defining the origin(s) of the structure. E.g. center of a circle, top corner of a rectangle, set of points of a polygon
        \param args Unused
        """

        ## Point(s) defining a structure
        self.origins = origins

    def validate(self, num_of_rows, num_of_cols):
        """!
        \brief Checks if a given point is inside the phantom

        \param num_of_rows Number of rows in the phantom
        \param num_of_cols Number of columns in the phantom

        \return An empty string if the point is inside the phantom; an error string otherwise
        """

        # x: cols, y:rows
        for point in self.origins:
            if ((point.x < 0 or point.x > num_of_cols - 1) or 
               (point.y < 0 or point.y > num_of_rows - 1)):
                return "The defined points are out of bounds of the phantom.\r\n"

        return ""

    def calculate_scattering_c0(self, amplitude, config):
        """!
        \brief Computes values for sound speed map used in k-Wave phantoms

        \param amplitude Amplitude of the scatterer
        \param config The parsed configuration

        \return The sound speed in the requested position
        """

        c0 = config.get("sound_speed_c0_m_per_s", 1540)

        scattering_c0 = c0 + 25 + 75 * amplitude

        if scattering_c0 > 1600:
            scattering_c0 = 1600

        if scattering_c0 < 1400:
            scattering_c0 = 1400

        return scattering_c0

    def fill_structure(self, phantom, pos_x, pos_y, scat_gain, sound_speed_map, density_map, config):
        """!
        \brief Defines the values inside a generic structure

        \param phantom  The 2-D array where the scatterers amplitude will be stored
        \param pos_x X coordinate of current scatterer
        \param pos_y Y coordinate of current scatterer
        \param scat_gain The gain of the scatterers inside the sphere
        \param sound_speed_map The 2-D array where the sound values will be stored
        \param density_map The 2-D array where the density values will be stored
        \param config The parsed configuration
        """

        phantom[pos_x][pos_y] = phantom[pos_x][pos_y] * scat_gain

        ## Type of phantom
        self.phantom_format = config["phantom_format"].lower()

        if self.phantom_format == "k_wave":
            scattering_c0 = self.calculate_scattering_c0(abs(phantom[pos_x][pos_y]), config)

            sound_speed_map[pos_x][pos_y] = scattering_c0
            density_map[pos_x][pos_y] = scattering_c0 / 1.5


class Circle(Structure):
    """!
    \brief Defines a circle inside a phantom
    """

    def __init__(self, origins, *args):
        """
        \brief Initializes a circle using the following inputs:

        \param origins One point defining the center of the circle (x, y)
        \param args One integer value containing the circle radius (so only args[0] is used)
        """

        ## Center (point) of the circle
        self.center = origins[0]

        ## Radius of the circle
        self.radius = args[0]

    def validate(self, num_of_rows, num_of_cols):
        """!
        \brief Validates the circle configuration

        \param num_of_rows Number of rows in the phantom
        \param num_of_cols Number of columns in the phantom

        \return An empty string if the circle configuration is valid; an error string otherwise
        """

        if (self.radius <= 0):
            return "Circle radius must be greater than zero"
        elif ((self.center.y + self.radius > num_of_rows - 1) or (self.center.x + self.radius > num_of_cols - 1) or
           (self.center.x - self.radius < 0) or (self.center.y - self.radius < 0)):
            return "The defined circle is out of bounds of the phantom.\r\n"
        else:
            return ""

    def fill_area(self, phantom, sound_speed_map, density_map, scat_gain, config):
        """!
        \brief Fills a circle

        \param phantom The 2-D array where the scatterers amplitude will be stored
        \param sound_speed_map The 2-D array where the sound values will be stored
        \param density_map The 2-D array where the density values will be stored
        \param scat_gain The gain of the scatterers inside the sphere
        \param config The parsed configuration
        """

        # Create a rectangle and, inside it, search for points that are inside the circle
        top_x = self.center.x - self.radius
        top_y = self.center.y - self.radius

        for x in range(top_x, top_x + 2*self.radius):
            if mod(x, 10) == 0:
                ut.log_message("Filling column " + str(x) + ". Range from " + str(top_x) + " to " + str(top_x + 2*self.radius), config.get("verbose", False))
            for y in range(top_y, top_y + 2*self.radius):
                if pow((x - self.center.x), 2) + pow((y - self.center.y), 2) <= pow(self.radius, 2):
                    self.fill_structure(phantom, x, y, scat_gain, sound_speed_map, density_map, config)


class Rectangle(Structure):
    """!
    \brief Rectangular structure
    """

    def __init__(self, origins, *args):
        """!
        \brief Defines the origin and dimensions of the rectangle

        \param origins Top left corner coordinates (x, y)
        \param args Rectangle dimensions - args[0]: horizontal length; args[1]: vertical length
        """

        ## Top-left corner of the rectangle
        self.top_left_corner = origins[0]

        ## Width of the rectangle
        self.horizontal_length = args[0]

        ## Height of the rectangle
        self.vertical_length = args[1]

    def validate(self, num_of_rows, num_of_cols):
        """!
        \brief Validates the configuration

        \param num_of_rows Number of rows in the phantom
        \param num_of_cols Number of columns in the phantom

        \return An empty string if the rectangle configuration is valid; an error string otherwise
        """

        if (self.horizontal_length <= 0 or self.vertical_length <= 0):
            return "Rectangle dimensions must be greater than zero"
        elif ((self.top_left_corner.y + self.vertical_length > num_of_rows - 1) or 
           (self.top_left_corner.x + self.horizontal_length > num_of_cols - 1) or
           (self.top_left_corner.x < 0) or (self.top_left_corner.y < 0)):
           return "The defined rectangle is out of bounds of the phantom.\r\n"
        else:
            return ""

    def fill_area(self, phantom, sound_speed_map, density_map, scat_gain, config):
        """!
        \brief Fills the area inside the rectangle

        \param phantom The 2-D array where the scatterers amplitude will be stored
        \param sound_speed_map The 2-D array where the sound values will be stored
        \param density_map The 2-D array where the density values will be stored
        \param scat_gain The gain of the scatterers inside the sphere
        \param config The parsed configuration
        """

        for x in range(self.top_left_corner.x, self.top_left_corner.x + self.horizontal_length):
            if mod(x, 10) == 0:
                ut.log_message("Filling column " + str(x) + ". Range from " + str(self.top_left_corner.x) + " to " + str(self.top_left_corner.x + self.horizontal_length), config.get("verbose", False))
            for y in range(self.top_left_corner.y, self.top_left_corner.y + self.vertical_length):
                self.fill_structure(phantom, x, y, scat_gain, sound_speed_map, density_map, config)


class Polygon(Structure):
    """!
    \brief Free-form polygon
    """

    def fill_area(self, phantom, sound_speed_map, density_map, scat_gain, config):
        """!
        \brief Fills the are inside the polygon

        \param phantom The 2-D array where the scatterers amplitude will be stored
        \param sound_speed_map The 2-D array where the sound values will be stored
        \param density_map The 2-D array where the density values will be stored
        \param scat_gain The gain of the scatterers inside the sphere
        \param config The parsed configuration
        """

        # Find max, min of x and y
        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0

        for point in self.origins:
            min_x = min(point.x, min_x)
            max_x = max(point.x, max_x)
            min_y = min(point.y, min_y)
            max_y = max(point.y, max_y)

        # Check if every pixel in this range is inside the polygon, if so, apply gain
        # This is done to reduce the are for test without looking for complex
        # algorithms to determine the area
        for x in range(min_x, max_x):
            if mod(x, 10) == 0:
                ut.log_message("Filling column " + str(x) + ". Range from " + str(min_x) + " to " + str(max_x), config.get("verbose", False))
            for y in range(min_y, max_y):
                point = Point((x, y))
                if point.in_polygon(self.origins): 
                    # Point is inside the polygon
                    self.fill_structure(phantom, point.x, point.y, scat_gain, sound_speed_map, density_map, config)


class SinglePoint(Structure):
    """!
    \brief A simple point inside the structure
    """

    def fill_area(self, phantom, sound_speed_map, density_map, scat_gain, config):
        """!
        \brief Define a value for the points

        \param phantom The 2-D array where the scatterers amplitude will be stored
        \param sound_speed_map The 2-D array where the sound values will be stored
        \param density_map The 2-D array where the density values will be stored
        \param scat_gain The gain of the scatterers inside the sphere
        \param config The parsed configuration
        """

        for point in self.origins:
            # Make sure there's a scatterer in this location
            if phantom[point.x][point.y] == 0:
                phantom[point.x][point.y] = 1

            self.fill_structure(phantom, point.x, point.y, scat_gain, sound_speed_map, density_map, config)


class Structure3d(object):
    """!
    \brief Base class for real 3-D structures (not 2-D structures replicated along the Z-axis)
    """

    def __init__(self, origins, *args):
        """!
        \brief Sets the origin

        \param origins One point defining the origin (e.g. center) of the structure (x, y, z)
        \param args Unused
        """

        ## Points defining the 3-D structure
        self.origins = origins

    def validate(self, num_of_rows, num_of_cols, num_of_z):
        """!
        \brief Checks if the structure origin is within boundaries

        \param num_of_rows Number of rows in the phantom
        \param num_of_cols Number of columns in the phantom
        \param num_of_z Number of slices in the phantom

        \return An empty string if the points positions are valid; an error string otherwise
        """

        # x: cols, y:rows, z:depth
        for point in self.origins:
            if ((point.x < 0 or point.x > num_of_cols - 1) or 
               (point.y < 0 or point.y > num_of_rows - 1)  or
               (point.z < 0 or point.z > num_of_z - 1)):
                return "The defined points are out of bounds of the phantom.\r\n"

        return ""


class Sphere(Structure, Structure3d):
    """!
    \brief Defines a sphere inside a phantom
    """

    def __init__(self, origins, *args):
        """!
        \brief Initializes a sphere using the following inputs:

        \param origins One point defining the center of the sphere (x, y, z)
        \param args One integer value containing the sphere radius (so only args[0] is used)
        """

        ## X, Y, Z coordinates of the center of the sphere
        self.center = origins[0]

        ## Radius of the sphere
        self.radius = args[0]

    def validate(self, num_of_rows, num_of_cols, num_of_z):
        """!
        \brief Validates the sphere configuration

        \param num_of_rows Number of rows in the phantom
        \param num_of_cols Number of columns in the phantom
        \param num_of_z Number of slices in the phantom

        \return An empty string if the sphere configuration is valid; an error string otherwise
        """

        if (self.radius <= 0):
            return "Sphere radius must be greater than zero"
        elif ((self.center.y + self.radius > num_of_rows - 1) or (self.center.x + self.radius > num_of_cols - 1)  or (self.center.z + self.radius > num_of_z - 1) or
           (self.center.x < self.radius) or (self.center.y < self.radius) or (self.center.z < self.radius)):
           return "The defined sphere is out of bounds of the phantom.\r\n"
        else:
            return ""

    def fill_volume(self, phantom, slice, sound_speed_map, density_map, scat_gain, config):
        """!
        \brief Fills an sphere

        \param phantom The 2-D array where the scatterers amplitude will be stored
        \param slice Current slice (0-based)
        \param sound_speed_map The 2-D array where the sound values will be stored
        \param density_map The 2-D array where the density values will be stored
        \param scat_gain The gain of the scatterers inside the sphere
        \param config The parsed configuration
        """

        # Create a cube and, inside it, search for points that are inside the sphere
        top_x = self.center.x - self.radius
        top_y = self.center.y - self.radius

        for x in range(top_x, top_x + 2*self.radius):
            if mod(x, 10) == 0:
                ut.log_message("Filling column " + str(x) + ". Range from " + str(top_x) + " to " + str(top_x + 2*self.radius), config.get("verbose", False))
            for y in range(top_y, top_y + 2*self.radius):
                if pow((x - self.center.x), 2) + pow((y - self.center.y), 2) + pow((slice - self.center.z), 2) <= pow(self.radius, 2):
                    self.fill_structure(phantom, x, y, scat_gain, sound_speed_map, density_map, config)
