"""
Tests for structure generation
Run tests with 'python -m unittest tests.test_structures'
"""

from mx_us_phantom import structures as struc
import unittest


class TestInPolygon(unittest.TestCase):
    """
    Tests regarding identifying if a point is inside a polygon
    """
    def test_point_outside__return_false(self):
        """
        Test a point not inside the polygon
        """

        point = struc.Point((3, 1))
        polygon = [struc.Point((0, 0)), struc.Point((0, 1)), struc.Point((1, 2)), struc.Point((2, 1)), struc.Point((2, 0))]
        is_inside = point.in_polygon(polygon)

        self.assertFalse(is_inside)

    def test_boundary_point__return_false(self):
        """
        Test a point that's right in the line
        """

        point = struc.Point((20, 5))
        polygon = [struc.Point((0, 0)), struc.Point((0, 10)), struc.Point((20, 10)), struc.Point((20, 0))]
        is_inside = point.in_polygon(polygon)

        self.assertFalse(is_inside)

    def test_point_inside__return_true(self):
        """
        Test a point that's inside the polygon
        """

        point = struc.Point((58.97, 20.5))
        polygon = [struc.Point((0, 0)), struc.Point((200, 309)), struc.Point((200, 0))]
        is_inside = point.in_polygon(polygon)

        self.assertTrue(is_inside)

    def test_point_marginally_inside__return_false(self):
        """
        Test a point that's a small distance inside the polygon
        """

        point = struc.Point((200, 308.999))
        polygon = [struc.Point((0, 0)), struc.Point((200, 309)), struc.Point((200, 0))]
        is_inside = point.in_polygon(polygon)

        self.assertFalse(is_inside)

    def test_concave_polygon_points_outside__return_false(self):
        """
        Test if points that are outside a concave polygon are properly detected
        """

        polygon = [struc.Point((2, 1)), struc.Point((88, 7)), struc.Point((144, 21)), struc.Point((100, 79)), struc.Point((59, 46)), struc.Point((7, 61)), struc.Point((44, 36))]
        point = struc.Point((26, 36))
        is_inside = point.in_polygon(polygon)

        self.assertFalse(is_inside)

        point = struc.Point((52, 58))
        is_inside = point.in_polygon(polygon)

        self.assertFalse(is_inside)

        point = struc.Point((260, 360))
        is_inside = point.in_polygon(polygon)

        self.assertFalse(is_inside)

    def test_concave_polygon_points_inside__return_true(self):
        """
        Test if points that are inside a concave polygon are properly detected
        """

        polygon = [struc.Point((2, 1)), struc.Point((88, 7)), struc.Point((144, 21)), struc.Point((100, 79)), struc.Point((59, 46)), struc.Point((7, 61)), struc.Point((44, 36))]
        point = struc.Point((39, 47))
        is_inside = point.in_polygon(polygon)

        self.assertTrue(is_inside)

        point = struc.Point((41, 7))
        is_inside = point.in_polygon(polygon)

        self.assertTrue(is_inside)

        point = struc.Point((99, 77))
        is_inside = point.in_polygon(polygon)

        self.assertTrue(is_inside)


class TestStructuresValidation(unittest.TestCase):
    """
    Tests for verifying if the structures methos are correct
    """
    def test_points_inside_and_on_boundaries__no_error(self):
        """
        Test single points on the phantom boundaries
        """

        point = struc.SinglePoint([struc.Point((0, 0))])
        validation_error = point.validate(512, 512)

        self.assertTrue(not validation_error)

        point = struc.SinglePoint([struc.Point((511, 511))])
        validation_error = point.validate(512, 512)

        self.assertTrue(not validation_error)

        point = struc.SinglePoint([struc.Point((0, 511))])
        validation_error = point.validate(512, 512)

        self.assertTrue(not validation_error)

        point = struc.SinglePoint([struc.Point((511, 0))])
        validation_error = point.validate(512, 512)

        self.assertTrue(not validation_error)

        point = struc.SinglePoint([struc.Point((100, 200))])
        validation_error = point.validate(512, 512)

        self.assertTrue(not validation_error)

    def test_points_outside_boundaries__errors_detected(self):
        """
        Test single points outside the phantom boundaries
        """

        point = struc.SinglePoint([struc.Point((-1, 0))])
        validation_error = point.validate(512, 512)

        self.assertFalse(not validation_error)

        point = struc.SinglePoint([struc.Point((511, -511))])
        validation_error = point.validate(512, 512)

        self.assertFalse(not validation_error)

        point = struc.SinglePoint([struc.Point((512, 512))])
        validation_error = point.validate(512, 512)

        self.assertFalse(not validation_error)

        point = struc.SinglePoint([struc.Point((600, 600))])
        validation_error = point.validate(512, 512)

        self.assertFalse(not validation_error)

    def test_rectangle_inside_boundaries__no_error(self):
        """
        Test rectangles inside the phantom boundaries
        """

        rec = struc.Rectangle([struc.Point((0, 0))], 511, 511)
        validation_error = rec.validate(512, 512)

        self.assertTrue(not validation_error)

        rec = struc.Rectangle([struc.Point((30, 80))], 51, 111)
        validation_error = rec.validate(512, 512)

        self.assertTrue(not validation_error)

        rec = struc.Rectangle([struc.Point((460, 400))], 51, 111)
        validation_error = rec.validate(512, 512)

        self.assertTrue(not validation_error)

        rec = struc.Rectangle([struc.Point((460, 400))], 51, 111)
        validation_error = rec.validate(512, 612)

        self.assertTrue(not validation_error)

    def test_rectangle_outside_boundaries__errors_detected(self):
        """
        Test rectangles outside the phantom boundaries
        """

        rec = struc.Rectangle([struc.Point((0, 0))], 512, 512)
        validation_error = rec.validate(512, 512)

        self.assertFalse(not validation_error)

        rec = struc.Rectangle([struc.Point((-30, 80))], 51, 111)
        validation_error = rec.validate(512, 512)

        self.assertFalse(not validation_error)

        rec = struc.Rectangle([struc.Point((460, -400))], 51, 111)
        validation_error = rec.validate(512, 512)

        self.assertFalse(not validation_error)

        rec = struc.Rectangle([struc.Point((860, 600))], 51, 111)
        validation_error = rec.validate(512, 612)

        self.assertFalse(not validation_error)

    def test_invalid_rectangle__errors_detected(self):
        """
        Test invalid rectangle
        """

        rec = struc.Rectangle([struc.Point((0, 0))], -512, 512)
        validation_error = rec.validate(512, 512)

        self.assertFalse(not validation_error)

        rec = struc.Rectangle([struc.Point((30, 80))], 51, -111)
        validation_error = rec.validate(512, 512)

        self.assertFalse(not validation_error)

        rec = struc.Rectangle([struc.Point((460, 400))], -51, -111)
        validation_error = rec.validate(512, 512)

        self.assertFalse(not validation_error)

        rec = struc.Rectangle([struc.Point((-60, -60))], -51, -111)
        validation_error = rec.validate(512, 612)

        self.assertFalse(not validation_error)

    def test_circle_inside_boundaries__no_error(self):
        """
        Test circles inside the phantom
        """

        circ = struc.Circle([struc.Point((10, 20))], 10)
        validation_error = circ.validate(64, 128)

        self.assertTrue(not validation_error)

        circ = struc.Circle([struc.Point((256, 256))], 256)
        validation_error = circ.validate(513, 513)

        self.assertTrue(not validation_error)

        circ = struc.Circle([struc.Point((256, 356))], 256)
        validation_error = circ.validate(613, 513)

        self.assertTrue(not validation_error)

    def test_circle_outside_boundaries__errors_detected(self):
        """
        Test circles outside the phantom
        """

        circ = struc.Circle([struc.Point((0, 0))], 10)
        validation_error = circ.validate(64, 128)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((30, 80))], 310)
        validation_error = circ.validate(256, 256)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((256, 256))], 256)
        validation_error = circ.validate(512, 512)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((-60, -60))], 10)
        validation_error = circ.validate(512, 612)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((500, 500))], 100)
        validation_error = circ.validate(512, 612)

        self.assertFalse(not validation_error)

    def test_invalid_circle__errors_detected(self):
        """
        Test invalid circle
        """

        circ = struc.Circle([struc.Point((0, 0))], 0)
        validation_error = circ.validate(64, 128)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((30, 80))], -10)
        validation_error = circ.validate(256, 256)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((-460, -400))], -51)
        validation_error = circ.validate(512, 512)

        self.assertFalse(not validation_error)

        circ = struc.Circle([struc.Point((-60, -60))], -1)
        validation_error = circ.validate(512, 612)

        self.assertFalse(not validation_error)

    def test_polygon_inside_phantom__no_error(self):
        """
        Test if a free form polygon is inside the boundaries of the phantom
        """

        polygon = [struc.Point((2, 1)), struc.Point((88, 7)), struc.Point((144, 21)), struc.Point((100, 79)), struc.Point((59, 46)), struc.Point((7, 61)), struc.Point((44, 36))]
        poly = struc.Polygon(polygon)
        validation_error = poly.validate(101, 145)

        self.assertTrue(not validation_error)
        
        polygon = [struc.Point((0, 0)), struc.Point((0, 1)), struc.Point((1, 2)), struc.Point((2, 1)), struc.Point((2, 0))]

        poly = struc.Polygon(polygon)
        validation_error = poly.validate(3, 3)

        self.assertTrue(not validation_error)

    def test_polygon_outside_phantom__errors_detected(self):
        """
        Test if a free form polygon is outside the boundaries of the phantom
        """

        polygon = [struc.Point((2, 1)), struc.Point((88, 7)), struc.Point((144, 21)), struc.Point((100, 79)), struc.Point((59, 46)), struc.Point((7, 61)), struc.Point((44, 36))]
        poly = struc.Polygon(polygon)
        validation_error = poly.validate(101, 144)

        self.assertFalse(not validation_error)
        
        polygon = [struc.Point((0, 0)), struc.Point((0, 1)), struc.Point((10, 2)), struc.Point((2, 1)), struc.Point((2, 0))]

        poly = struc.Polygon(polygon)
        validation_error = poly.validate(3, 3)

        self.assertFalse(not validation_error)

        polygon = [struc.Point((0, 0)), struc.Point((0, 1)), struc.Point((10, -2)), struc.Point((2, 1)), struc.Point((2, 0))]

        poly = struc.Polygon(polygon)
        validation_error = poly.validate(3, 3)

        self.assertFalse(not validation_error)


class CheckFilledArea(unittest.TestCase):
    """
    Verify that the area of the structure is correctly filled
    """
    def setUp(self):
        self.configuration = {
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

        self.num_of_rows = 20
        self.num_of_cols = 20
        self.phantom = [[1 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]
        self.sound_speed_map = [[1 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]
        self.density_map = [[1 for y in range(self.num_of_rows)] for x in range(self.num_of_cols)]

    def test_fill_SinglePoint__only_specified_points_filled(self):
        """
        Check that a few points are filled
        """

        ix = [0, 1, 1, 1, 3]
        iy = [0, 0, 1, 2, 2]
        gain = [4, 9, 3, 5, 6]

        points = []

        for i in range(len(ix)):
            points.append(struc.SinglePoint([struc.Point((ix[i], iy[i]))]))

        for i in range(len(ix)):
            points[i].fill_area(self.phantom, self.sound_speed_map, self.density_map, gain[i], self.configuration)

        num_of_filled_points = 0

        for x in range(self.num_of_cols):
            for y in range(self.num_of_rows):
                for i in range(len(ix)):
                    if (x == ix[i] and y == iy[i]):
                        if (self.phantom[x][y] == gain[i]):
                            num_of_filled_points = num_of_filled_points + 1

        self.assertTrue(num_of_filled_points == len(ix))

    def test_fill_triangle__only_specified_points_filled(self):
        """
        Check that a few points are filled inside a triangle
        """

        triangle = struc.Polygon([struc.Point((5, 0)), struc.Point((9, 4)), struc.Point((0, 4))])

        gain = 7
        triangle.fill_area(self.phantom, self.sound_speed_map, self.density_map, gain, self.configuration)

        num_of_filled_points = 0

        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                if (self.phantom[x][y] == gain):
                    num_of_filled_points = num_of_filled_points + 1
        
        self.assertTrue(num_of_filled_points == 12) # Magic number based on previous tests

    def test_fill_rectangle__only_specified_points_filled(self):
        """
        Check that a few points are filled inside a rectangle
        """

        rectangle = struc.Rectangle([struc.Point((5, 5))], 4, 3)

        gain = 7
        rectangle.fill_area(self.phantom, self.sound_speed_map, self.density_map, gain, self.configuration)

        num_of_filled_points = 0

        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                if (self.phantom[x][y] == gain):
                    num_of_filled_points = num_of_filled_points + 1
        
        self.assertTrue(num_of_filled_points == 12) # Magic number based on previous tests

    def test_fill_circle__only_specified_points_filled(self):
        """
        Check that a few points are filled inside a circle
        """

        circle = struc.Circle([struc.Point((10, 8))], 5)

        gain = 7
        circle.fill_area(self.phantom, self.sound_speed_map, self.density_map, gain, self.configuration)

        num_of_filled_points = 0

        for y in range(self.num_of_rows):
            for x in range(self.num_of_cols):
                if (self.phantom[x][y] == gain):
                    num_of_filled_points = num_of_filled_points + 1

        self.assertTrue(num_of_filled_points == 79) # Magic number based on previous tests


if __name__ == '__main__':
    unittest.main()
