import unittest
import utm
import numpy as np

import orchard


class TestGrid(unittest.TestCase):

    def setUp(self):
        # Setup mock data for latitude and longitude
        self.latitude = np.array([40.689202777778, 40.689202777778])
        self.longitude = np.array([-74.044219444444, -74.044219444444])

        # Initialize Grid object
        self.grid = orchard.Grid(self.latitude, self.longitude)

    def test_init(self):
        # Test the initialization of the Grid object
        self.assertIsNotNone(self.grid.latitude)
        self.assertIsNotNone(self.grid.longitude)
        self.assertIsNotNone(self.grid.utm_centre)

    def test_nearest_neighbour(self):
        # Test the nearest_neighbour method
        utm_points = np.column_stack(utm.from_latlon(self.latitude, self.longitude)[:2])
        distances, indices = self.grid.nearest_neighbour(utm_points)

        self.assertEqual(len(distances), len(utm_points))
        self.assertEqual(len(indices), len(utm_points))

    def test_rot_matrix(self):
        # Test the rot_matrix method
        angle = np.pi / 4  # 45 degrees
        matrix = self.grid.rot_matrix(angle)

        self.assertEqual(matrix.shape, (2, 2))
        self.assertAlmostEqual(matrix[0, 0], np.cos(angle))
        self.assertAlmostEqual(matrix[1, 0], np.sin(angle))

    def test_utm_to_grid(self):
        # Test the utm_to_grid method
        utm_points = np.column_stack(utm.from_latlon(self.latitude, self.longitude)[:2])
        x, y = self.grid.utm_to_grid(utm_points)

        self.assertEqual(len(x), len(utm_points))
        self.assertEqual(len(y), len(utm_points))

    def test_calculate_grid_angle(self):
        # Test the calculate_grid_angle method
        utm_points = np.column_stack(utm.from_latlon(self.latitude, self.longitude)[:2])
        angle = self.grid.calculate_grid_angle(utm_points)

        self.assertIsInstance(angle, float)

    # ... Continue with other methods

if __name__ == '__main__':
    unittest.main()
