import cv2
import numpy as np

class ROIEvaluator:
    def evaluate_and_visualize_rois(self, plant_objs, frame):
        rois = self.evaluate_rois(plant_objs,frame)
        return self.visualize_rois(frame,rois)
    def evaluate_rois(self, plant_objs, frame):
        pass
    
    def visualize_rois(self, frame):
        pass

class SimpleROI(ROIEvaluator):
    
    def evaluate_and_visualize_rois(self, plant_objs, frame):
        rois = self.evaluate_rois(plant_objs,frame)
        return self.visualize_rois(roi_points=rois,frame=frame)
    
    def evaluate_rois(self, plant_objs, frame):
        type = "center"
        sides = 4
        n = len(plant_objs)  # Number of ROIs
        if n == 0:
         n = 9
        x_offset = 65
        y_offset_initial = -20
        x_initial = -300
        y_offset = 12

        rois = []
        for i in range(n):
            y_offset *= -1  # Alternating y offset
            offset = (x_initial + x_offset * i, y_offset_initial + y_offset)
            roi_points = self.get_single_roi(frame, type, sides, 20,offset)
            rois.append(roi_points)

        return rois
    

    def visualize_rois(frame, roi_points):
        # Check if frame is a valid image
        if not isinstance(frame, np.ndarray):
            raise TypeError("Provided frame is not a valid numpy array.")

        for points in roi_points:
            # Ensure points form a valid polygon
            if points and isinstance(points, list):
                roi_array = np.array(points, dtype=np.int32)
                cv2.polylines(frame, [roi_array], isClosed=True, color=(0, 255, 0), thickness=2)
            else:
                print("Invalid ROI points:", points)
        return frame

    
    def visualize_rois(self,frame, roi_points):
        """Draw polygons on the frame from given points."""
        for points in roi_points:
            
            # Ensure points form a valid polygon
            if points and isinstance(points, list):
                # Ensure points are in the correct format
                if not points:
                    print("Warning: Empty ROI points.")
                    continue
                roi_array = np.array(points, dtype=np.int32)
                # print(f"Drawing ROI with points: {roi_array}")  # Debug print

                # Draw the polygon on the frame
                cv2.polylines(frame, [roi_array], isClosed=True, color=(0, 255, 0), thickness=2)
            else:
                print("Invalid ROI points:", points)

        return frame

    def get_single_roi(self, frame, type, num_sides=4, size=20, offset=(0, 0)):
        if type == "center":
            center = self.get_center_frame(frame, size, size, offset)
            return self.get_roi_polygon(center, num_sides)
        else:
            print("Unknown type")
            return []

    def get_roi_polygon(self, center, num_sides):

    
        (x1, y1), (x2, y2) = center
        width = x2 - x1
        height = y2 - y1
        center_point = (x1 + width // 2, y1 + height // 2)
        radius = min(width, height) // 2
        angle = 2 * np.pi / num_sides

        roi_points = []
        for i in range(num_sides):
            x = int(center_point[0] + radius * np.cos(i * angle))
            y = int(center_point[1] + radius * np.sin(i * angle))
            roi_points.append((x, y))

        return roi_points

    def get_center_frame(self, frame, roi_width, roi_height, offset=(0, 0)):
        # print(f"Frame Width: {type(frame.shape[1])}, ROI Width: {type(roi_width)}, ROI Height: {type(roi_height)}, Offset[0]: {type(offset[0])}")
        frame_height, frame_width = frame.shape[:2]
        x1 = (frame_width - roi_width) // 2 + offset[0]
        y1 = (frame_height - roi_height) // 2 + offset[1]
        x2 = x1 + roi_width
        y2 = y1 + roi_height
        return [(x1, y1), (x2, y2)]

    
