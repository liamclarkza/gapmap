import unittest
import utm
import numpy as np
from orchard.grid import Grid


class TestGrid(unittest.TestCase):

    def setUp(self):
        # Initialize test data
        self.latitude = np.array([[-32.3286795], [-32.3286305], [-32.3288194], [-32.3288021],
                         [-32.3285440], [-32.3286132], [-32.3289449], [-32.3284577],
                         [-32.3286377], [-32.3285945], [-32.3286925], [-32.3286844],
                         [-32.3288684], [-32.3284803], [-32.3289867], [-32.3288454],
                         [-32.3287944], [-32.3288064], [-32.3287761], [-32.3286709],
                         [-32.3288872], [-32.3289535], [-32.3287343], [-32.3285570],
                         [-32.3286507], [-32.3288598], [-32.3287660], [-32.3285022],
                         [-32.3285252], [-32.3288476], [-32.3289189], [-32.3287473],
                         [-32.3287264], [-32.3286132], [-32.3285137], [-32.3287377],
                         [-32.3285570], [-32.3285711], [-32.3288324], [-32.3285844],
                         [-32.3289131], [-32.3287055], [-32.3284939], [-32.3288583],
                         [-32.3289290], [-32.3285030], [-32.3289723], [-32.3285699],
                         [-32.3287934], [-32.3285189]])
        
        self.longitude = np.array([[18.8256509], [18.8259345], [18.8257375], [18.8259464],
                          [18.8258292], [18.8258683], [18.8257817], [18.8257102],
                          [18.8257273], [18.8258105], [18.8257086], [18.8259086],
                          [18.8257239], [18.8257719], [18.8256968], [18.8255966],
                          [18.8258791], [18.8256815], [18.8258241], [18.8258482],
                          [18.8257919], [18.8258377], [18.8256305], [18.8258904],
                          [18.8257885], [18.8256628], [18.8257596], [18.8256322],
                          [18.8257630], [18.8258603], [18.8256407], [18.8256934],
                          [18.8258288], [18.8255983], [18.8257036], [18.8258925],
                          [18.8256118], [18.8256739], [18.8258071], [18.8257409],
                          [18.8259141], [18.8257749], [18.8258322], [18.8259362],
                          [18.8257103], [18.8258980], [18.8256254], [18.8259532],
                          [18.8256135], [18.8259596]])
        
        self.grid = Grid(self.latitude, self.longitude)


    def test_utm_conversion(self):
        # Check UTM zone number
        self.assertEqual(34, self.grid.zone_number, msg="UTM zone number should be 34")
        
        # Check UTM zone letter
        self.assertEqual('H', self.grid.zone_letter, msg="UTM zone letter should be 'H'")
        
        # Check UTM center coordinates
        for i, utm_coord in enumerate((295347.53488333, 6421050.8008741)):
            self.assertAlmostEqual(utm_coord, self.grid.utm_centre[i],
                                   msg=f"UTM coordinate {i+1} should match")
        

    def test_nearest_neighbour(self):
        # Check the number of nearest neighbors
        self.assertEqual(len(self.grid.nn_indices), 50, msg="Number of nearest neighbors should be 50")
        self.assertEqual(len(self.grid.nn_dists), 50, msg="Number of nearest neighbor distances should be 50")
        
        # Check that all nearest neighbor distances are less than 7
        for dist in self.grid.nn_dists[:, 1]:
            self.assertLess(dist, 7, msg="Nearest neighbor distance should be less than 7")


    def test_grid_angle(self):
        self.assertAlmostEqual(1.3523934, self.grid.grid_angle, msg="Calculated grid angle should match")

    def test_grid_points(self):
        # Check gridded x and y coordinates
        grid_x = [0.9337144, 12.5282774, -12.2138883, -5.6985350, 19.5051182, 12.9186193,
             -24.7537689, 26.1553653, 7.1391494, 13.6468460, 0.8175054, 6.1433138,
             -17.7969686, 25.0937110, -31.1484467, -18.1527826, -6.3671853, -12.0598261,
             -5.6197192, 6.2532990, -18.3088698, -24.4336900, -5.4257802, 19.4668277,
             7.1008634, -18.2306047, -5.9674098, 19.6233486, 20.0570938, -12.5186371,
             -25.0913200, -5.4262117, -0.1593621, 6.9071209, 19.9738124, 0.0412003,
             13.2638533, 13.1270762, -12.0651534, 13.1856017, -18.3791351, 0.8927701,
             24.9707298, -11.9817934, -24.6300741, 25.4551246, -31.1863980, 19.4749332,
             -12.1729455, 25.1132302]
        
        grid_y = [12.0818584, -12.5813408, 0.4897754, -18.1699439, -0.6785945, -6.0706845,
             -6.8452817, 12.4724140, 6.1877233, -0.2918772, 6.4616745, -11.6250094,
             0.4491901, 6.2344959, -0.1734598, 12.6996628, -11.8103923, 5.9544098,
             -6.2982717, -5.7446767, -6.2654759, -12.1945277, 12.5113463, -6.6190202,
             0.2473031, 6.2650666, -0.1319709, 18.4421537, 5.8714025, -11.4853298,
             6.7373339, 6.4153896, -5.4250282, 18.6331024, 11.6078041, -11.5496025,
             18.8716448, 12.8200281, -6.2191941, 6.3410627, -18.1253628, 0.0546310,
             0.3606786, -18.7104052, 0.1044177, -5.8983616, 6.7369025, -12.7032155,
             12.5169888, -11.9514334]
        
        for i, (x, y) in enumerate(zip(grid_x, grid_y)):
            self.assertAlmostEqual(x, self.grid.x[i],
                                   msg=f"Grid x coordinate {i+1} should match")
            self.assertAlmostEqual(y, self.grid.y[i],
                                   msg=f"Grid y coordinate {i+1} should match")

    def test_grid_row_col(self):
        # Check grid rows and columns
        rows = [5, 1, 3, 0, 3, 2, 2, 5, 4, 3,
                4, 1, 3, 4, 3, 5, 1, 4, 2, 2,
                2, 1, 5, 2, 3, 4, 3, 6, 4, 1,
                4, 4, 2, 6, 5, 1, 6, 5, 2, 4,
                0, 3, 3, 0, 3, 2, 4, 1, 5, 1]
        
        cols = [5, 7, 3, 4, 8, 7, 1, 9, 6, 7,
                5, 6, 2, 9, 0, 2, 4, 3, 4, 6,
                2, 1, 4, 8, 6, 2, 4, 8, 8, 3,
                1, 4, 5, 6, 8, 5, 7, 7, 3, 7,
                2, 5, 9, 3, 1, 9, 0, 8, 3, 9]
        
        self.assertListEqual(rows, list(self.grid.rows), msg="Grid rows should match")
        self.assertListEqual(cols, list(self.grid.cols), msg="Grid columns should match")

    
    def test_detect_missing(self):
        # Check for missing rows and columns
        missing_rows_cols = [[1, 2], [5, 6]]
        for expected, got in zip(missing_rows_cols, self.grid.detect_missing_rows_cols()):
            self.assertListEqual(expected, list(got), msg="Missing rows/columns should match")

        # Check for missing points
        missing_points = [[-18.3440024, -11.8399287], [7.0231351, 12.4509432]]
        for expected, got in zip(missing_points, self.grid.detect_missing_points()):
            for expected_i, got_i in zip(expected, got):
                self.assertAlmostEqual(expected_i, got_i, msg="Missing points should match")

        # Check for missing latitude and longitude pairs
        missing_lat_lon = [[-32.3288994, 18.8258493], [-32.3286254, 18.8256624]]
        for expected, got in zip(missing_lat_lon, self.grid.detect_missing_lat_lon()):
            for expected_i, got_i in zip(expected, got):
                self.assertAlmostEqual(expected_i, got_i, msg="Missing latitude and longitude pairs should match")

if __name__ == '__main__':
    unittest.main()
