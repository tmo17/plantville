import numpy as np


def get_roi_function():
    """
    Takes in a frame and returns a function.
    The returned function will take the number of points and a pair of opposing corner points
    to define a regular polygon ROI within those bounds.
    """

    # TODO:  Implemement a further function that gets multiple ROIs then makes the polygon below
    # - eventually replacing that with a better function from a library
    # Validate the input frame

    def roi_function(num_sides, corner_points):
        """
        Takes the number of sides for a polygon and two corner points for bounding the polygon.
        Returns an array of points defining the ROI polygons.
        """
        if num_sides < 3:
            raise ValueError(
                "At least three sides are required to define a polygon")
        if not all(
                isinstance(point, tuple) and len(point) == 2
                for point in corner_points):
            raise ValueError(
                "Corner points must be tuples of (x, y) coordinates")
        if len(corner_points) != 2:
            raise ValueError("Exactly two corner points are required")

        # Calculate the center and radius of the bounding circle for the polygon
        (x1, y1), (x2, y2) = corner_points
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius = min(abs(x2 - x1), abs(y2 - y1)) / 2

        # Generate points for the polygon
        angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False)
        points = [(int(center_x + radius * np.cos(angle)),
                   int(center_y + radius * np.sin(angle))) for angle in angles]

        # Make sure to close the polygon by appending the first point at the end
        points.append(points[0])

        return points

    return roi_function


frame = np.random.randint(255, size=(100, 100, 3),
                          dtype=np.uint8)  # Dummy frame for example

# Get the function to compute ROI
compute_roi = get_roi_function()

# Define the number of sides for the polygon and the bounding box's opposite corners
num_sides = 3  # For a triangle
corner_points = [(0, 0), (100, 100)]  # Bounding box corners

# Get the ROI points for the first polygon
roi_points_1 = compute_roi(num_sides, corner_points)

num_sides = 4  # For a square
corner_points = [(50, 50), (100, 100)]  # Another bounding box corners

# Get the ROI points for the second polygon
roi_points_2 = compute_roi(num_sides, corner_points)

# List of all ROIs
all_rois = [roi_points_1, roi_points_2]

print(all_rois)
