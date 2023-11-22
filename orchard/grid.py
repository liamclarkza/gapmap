import utm
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from scipy.signal import correlate2d
from typing import Tuple

class Grid:
    def __init__(self, latitude: np.ndarray, longitude: np.ndarray):
        """
        Initialises the Grid object with latitude and longitude arrays.

        Args:
            latitude (np.ndarray): Array of latitude values.
            longitude (np.ndarray): Array of longitude values.
        """
        self.latitude = latitude
        self.longitude = longitude

        # Convert lat/lon to UTM coordinates
        easting, northing, self.zone_number, self.zone_letter = utm.from_latlon(self.latitude, self.longitude)
        utm_points = np.column_stack((easting, northing))
        self.utm_centre = np.mean(utm_points, axis=0)

        # Calculate grid center, nearest neighbors, and grid angle
        self.nn_dists, self.nn_indices = self.nearest_neighbour(utm_points)
        self.grid_angle = self.calculate_grid_angle(utm_points)

        # Convert UTM points to grid coordinates
        self.x, self.y = self.utm_to_grid(utm_points)

        # Label grid points with row and column numbers
        self.rows, self.cols = self.label_grid_points(self.x, self.y)


    @staticmethod
    def nearest_neighbour(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates the nearest neighbour for each point in a given array.

        Uses the NearestNeighbors class from sklearn.neighbors to find and return the distances
        and indices of the nearest neighbours for each point in the array.

        Args:
            points (np.ndarray): Array of points for which to find the nearest neighbours.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of arrays containing distances to, and indices of, 
                                           the nearest neighbours.
        """
        nbrs = NearestNeighbors(n_neighbors=2, algorithm='auto').fit(points)
        return nbrs.kneighbors(points)
    

    @staticmethod
    def rot_matrix(angle: float) -> np.ndarray:
        """
        Creates a 2D rotation matrix for a given angle.

        Args:
            angle (float): The angle in radians for which the rotation matrix is to be created.

        Returns:
            np.ndarray: A 2x2 numpy array representing the rotation matrix.
        """
        return np.array([[np.cos(angle), -np.sin(angle)], 
                         [np.sin(angle),  np.cos(angle)]])
    

    def utm_to_grid(self, utm_points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts UTM coordinates to grid coordinates.

        Args:
            utm_points (np.ndarray): Array of UTM coordinates.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of arrays representing the x and y coordinates in the grid.
        """
        x, y = (self.rot_matrix(-self.grid_angle) @ (utm_points - self.utm_centre).T)
        return x, y
    

    def calculate_grid_angle(self, utm_points: np.ndarray) -> float:
        """
        Calculates the grid angle based on UTM points.

        Determines the angle along which rows and columns of points align in the first quadrant using 
        nearest neighbours.

        Args:
            utm_points (np.ndarray): Array of UTM coordinates.

        Returns:
            float: The median angle in radians of lines connecting each point with its nearest neighbour.
        """
        delta = np.subtract(utm_points[self.nn_indices[:,0]], utm_points[self.nn_indices[:,1]])
        angles = np.arctan2(delta[:,1], delta[:,0]) % (np.pi/2)
        return np.median(angles)


    def grid_to_latlon(self, grid_points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts grid coordinates back to latitude and longitude.

        Args:
            grid_points (np.ndarray): Array of grid coordinates.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of arrays containing the latitude and longitude values.
        """
        utm_points = (self.rot_matrix(self.grid_angle) @ grid_points.T).T + self.utm_centre
        latitude, longitude = utm.to_latlon(utm_points[:,0], utm_points[:,1], self.zone_number, self.zone_letter)
        return latitude, longitude
    

    def label_grid_points(self, x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Assigns grid positions to rows and columns.

        DBSCAN clustering is used to group x and y coordinates into rows and columns, 
        respectively.

        Args:
            x (np.ndarray): Array of x coordinates on the grid.
            y (np.ndarray): Array of y coordinates on the grid.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of arrays containing row and column labels for each point.
        """
        def sort_cluster_labels(coords, labels):
            cluster_medians = {c: np.median(coords[labels == c]) for c in np.unique(labels)}
            sorted_clusters = sorted(cluster_medians, key=cluster_medians.get)
            cluster_to_label = {c: i for i, c in enumerate(sorted_clusters)}
            return np.array([cluster_to_label[c] for c in labels])

        eps = np.min(self.nn_dists[:,1])/2
        dbscan = DBSCAN(eps=eps, min_samples=2, metric='manhattan')
        rows = sort_cluster_labels(y, dbscan.fit(y.reshape((-1,1))).labels_)
        cols = sort_cluster_labels(x, dbscan.fit(x.reshape((-1,1))).labels_)
        return rows, cols


    def detect_missing_rows_cols(self) -> np.ndarray:
        """
        Identifies missing rows and columns in the grid.

        Returns:
            np.ndarray: Array of coordinates (row, col) where trees are missing.
        """
        def flood_fill(grid, x, y, fill_value):
            # Recursive flood fill algorithm
            if x < 0 or x >= grid.shape[0] or y < 0 or y >= grid.shape[1]:
                return
            if grid[x, y] != 0:
                return
            grid[x, y] = fill_value
            flood_fill(grid, x+1, y, fill_value)
            flood_fill(grid, x-1, y, fill_value)
            flood_fill(grid, x, y+1, fill_value)
            flood_fill(grid, x, y-1, fill_value)

        # Create a grid representation where each tree's position is marked as 1
        original_grid = np.zeros((np.max(self.rows)+2, np.max(self.cols)+2))
        for r, c, in zip(self.rows, self.cols):
            original_grid[r+1,c+1] = 1

        # Copy the original grid and apply flood fill to find unoccupied regions
        grid = original_grid.copy()
        flood_fill(grid, 0,0,-1)
        grid[grid!=-1] = 1
        grid[grid==-1] = 0

        # Define a kernel for morphological filling.
        # If the result of a correlation with this filter at some location is 3 or more
        # we fill set the centre to be a tree. Basically, if a coordinate is surrounded
        # by 3 or more trees, I treat it as a missing tree.
        kernel = np.array([
            [0,1,0],
            [1,0,1],
            [0,1,0]
        ])
        grid = grid[1:-1, 1:-1]

        # Iteratively correlate with kernel to fill in gaps.
        # Repeat until no change observed between previous and current iteration.
        previous_grid = np.zeros_like(grid)
        while np.any(previous_grid != grid):
            previous_grid = grid.copy()
            correlated = correlate2d(grid, kernel, mode='same')
            grid[correlated>2] = 1

        # Identify the missing coordinates by comparing with the original grid
        missing = grid - original_grid[1:-1, 1:-1]
        missing_coords = np.array(np.nonzero(missing)).T
        return missing_coords


    def detect_missing_points(self) -> np.ndarray:
        """
        Detects and returns the grid x and y coordinates of missing trees.

        Returns:
            np.ndarray: Array of (x, y) grid positions where points are missing.
        """
        grid_table = {(r, c):(x, y) for r, c, x, y in zip(self.rows, self.cols, self.x, self.y)}
        missing = []
        for r, c in self.detect_missing_rows_cols():
            neighbours = [grid_table[pos] for pos in ((r-1,c), (r+1,c), (r,c-1), (r,c+1)) if pos in grid_table]
            missing.append(np.median(neighbours, axis=0))
        return np.array(missing)


    def detect_missing_lat_lon(self) -> np.ndarray:
        """
        Detects and returns the latitude and longitude of missing trees.

        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of arrays containing latitude and longitude 
            respectively for missing trees.
        """
        missing_grid_points = self.detect_missing_points()
        return np.column_stack(self.grid_to_latlon(missing_grid_points))
