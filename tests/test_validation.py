"""
Tests for configuration validation
Run tests with 'python -m unittest tests.test_validation'
"""

from mx_us_phantom import config_validation as cfg_val
import unittest


class TestConfigValidation(unittest.TestCase):
    """
    Verify that configuration validation is properly done
    """
    def test_valid_config__no_errors(self):
        """
        Test with a valid configuration
        """
        configuration = {
            "rows_y":512,
            "cols_x":512,
            "distribution":"rayleigh",
            "perc_of_scatterers":50,
            "phantom_format":"effec_scatterers",
            "structures": [
                { "type":"circle", "center_xy":[ 20, 30 ], "radius":10, "scat_gain":3 },
                { "type":"rectangle", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 },
                { "type":"free_polygon", "vertices_xy":[ [200, 200], [400, 200], [400, 400] ], "scat_gain":1 },
                { "type":"points", "coordinates_xy":[ [80, 90], [85, 85] ], "scat_gain":2 }
            ]
        } 
        
        validation_error = cfg_val.validate_configuration(configuration)
        
        self.assertEqual(validation_error, "")

    def test_parameters_missing__errors_detected(self):
        """
        Test with empty configuration
        """
        configuration = { }

        with self.assertRaises(Exception) as context:
            cfg_val.validate_configuration(configuration)

        self.assertTrue("One of more parameters is missing in the configuration file" in str(context.exception))
        self.assertTrue("\"rows_y\" is missing" in str(context.exception))
        self.assertTrue("\"cols_x\" is missing" in str(context.exception))
        self.assertTrue("\"distribution\" is missing" in str(context.exception))
        self.assertTrue("\"perc_of_scatterers\" is missing" in str(context.exception))
        self.assertTrue("\"phantom_format\" is missing" in str(context.exception))

    def test_invalid_single_parameters__errors_detected(self):
        """
        Test with invalid parameters: distribution and scatterers percentage
        """
        configuration = {
            "rows_y":512,
            "cols_x":512,
            "distribution":"gamma",
            "perc_of_scatterers":-50,
            "phantom_format":"effec_scatterers",
            "structures": [
                { "type":"circle", "center_xy":[ 20, 30 ], "radius":10, "scat_gain":3 },
                { "type":"rectangle", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 }
            ]
        } 
        
        validation_error = cfg_val.validate_configuration(configuration)
        
        self.assertNotEqual(validation_error, "")
        self.assertIn("Supported distributions are", validation_error)
        self.assertIn("Percentage of scatterers should be", validation_error)

    def test_invalid_structure_define__errors_detected(self):
        """
        Test that a non-supported structure is detected
        """
        configuration = {
            "rows_y":512,
            "cols_x":512,
            "distribution":"gamma",
            "perc_of_scatterers":-50,
            "phantom_format":"effec_scatterers",
            "structures": [
                { "type":"square", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 }
            ]
        } 
        
        validation_error = cfg_val.validate_configuration(configuration)
        
        self.assertNotEqual(validation_error, "")
        self.assertIn("The structure of type", validation_error)
        self.assertIn("Supported structures are", validation_error)

    def test_valid_structures_only__no_errors(self):
        """
        Test that all supported structures are accepted
        """
        configuration = {
            "rows_y":512,
            "cols_x":512,
            "distribution":"rayleigh",
            "perc_of_scatterers":50,
            "phantom_format":"effec_scatterers",
            "structures": [
                { "type":"circle", "center_xy":[ 20, 30 ], "radius":10, "scat_gain":3 },
                { "type":"rectangle", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 },
                { "type":"free_polygon", "vertices_xy":[ [200, 200], [400, 200], [400, 400] ], "scat_gain":0 },
                { "type":"points", "coordinates_xy":[ [80, 90], [85, 85] ], "scat_gain":2 }
            ]
        } 
        
        validation_error = cfg_val.validate_configuration(configuration)
        
        self.assertEqual(validation_error, "")

    def test_k_wave_parameters_missing__errors_detected(self):
        """
        Test that all supported structures are accepted
        """
        configuration = {
            "rows_y":512,
            "cols_x":512,
            "distribution":"rayleigh",
            "perc_of_scatterers":50,
            "phantom_format":"k_wave",
            "structures": [
                { "type":"circle", "center_xy":[ 20, 30 ], "radius":10, "scat_gain":3 },
                { "type":"rectangle", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 },
                { "type":"free_polygon", "vertices_xy":[ [200, 200], [400, 200], [400, 400] ], "scat_gain":0 },
                { "type":"points", "coordinates_xy":[ [80, 90], [85, 85] ], "scat_gain":2 }
            ]
        } 

        with self.assertRaises(Exception) as context:
            cfg_val.validate_configuration(configuration)

        self.assertTrue("One of more parameters is missing in the configuration file" in str(context.exception))
        self.assertTrue("\"sound_speed_c0_m_per_s\" is missing" in str(context.exception))
        self.assertTrue("\"density_rho0_kg_per_m3\" is missing" in str(context.exception))

    def test_3d_effec_scatterers__not_accepted(self):
        """
        Test that all supported structures are accepted
        """
        configuration = {
            "rows_y":512,
            "cols_x":512,
            "depth_z":5,
            "distribution":"rayleigh",
            "perc_of_scatterers":50,
            "phantom_format":"effec_scatterers",
            "structures": [
                { "type":"circle", "center_xy":[ 20, 30 ], "radius":10, "scat_gain":3 },
                { "type":"rectangle", "top_left_corner_xy":[ 50, 60 ], "length_x":20, "length_y":30, "scat_gain":4 },
                { "type":"free_polygon", "vertices_xy":[ [200, 200], [400, 200], [400, 400] ], "scat_gain":0 },
                { "type":"points", "coordinates_xy":[ [80, 90], [85, 85] ], "scat_gain":2 }
            ]
        } 
        
        validation_error = cfg_val.validate_configuration(configuration)
        
        self.assertNotEqual(validation_error, "")
        self.assertIn("effec_scatterers only supports 2-D phantoms", validation_error)


if __name__ == '__main__':
    unittest.main()
