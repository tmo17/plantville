import numpy as np
import cv2 
from typing import List



class Analytic:
    def __init__(self, name = "Default",description="Default"):
        self.name = name 
        self.description = description

    def evaluate_analytic(self, frame, rois):
        raise NotImplementedError("This method should be overridden by subclasses")




class GreennessAnalytic(Analytic):  # Assuming inheritance from Analytic
    def __init__(self):
        description = "Greenness ratio of pixels in the ROI with green vs. without"
        name = "Greenness ratio"
        super().__init__(name, description)  # Corrected super() usage


    
    def evaluate_analytic(self, frame, rois):
        
        analytic_values = []

        for roi_points in rois:
            analytic_values.append(self.evaluate_greenness(frame,roi_points))

        return analytic_values


    def evaluate_greenness(self,frame, roi_points):
        # Mask for Green Pixels
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (36, 25, 25), (86, 255, 255))

        roi_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        roi_polygon = np.array([roi_points], dtype=np.int32)

        # Get Region and mask over region
        cv2.fillPoly(roi_mask, roi_polygon, 255)
        masked_region = cv2.bitwise_and(mask, mask, mask=roi_mask)


        # Calculate ratio of Green to to No Green Pixels
        green_ratio = 0
        total_roi_area = cv2.countNonZero(roi_mask)
        if total_roi_area > 0:
            green_ratio = cv2.countNonZero(masked_region) / total_roi_area
        
        return green_ratio

# # Example usage
# frame = cv2.imread('path_to_your_image.jpg')
# roi_points = [[100, 100], [150, 100], [150, 150], [100, 150]]  # Define your ROI points
# greenness = evaluate_greenness(frame, roi_points)
# print("Greenness ratio:", greenness)

            



    

class CropAnalytics:
    def __init__(self,analytics:List[Analytic] =[]):
        self.analytics = analytics if analytics is not None else []
    
    def add_analytic(self,new_analytic:Analytic):
        self.analytics.append(new_analytic)

    def run_analytics(self, frame, rois):
        results = {}
        for analytic in self.analytics:
            result = analytic.evaluate_analytic(frame, rois)
            results[analytic.name] = result
        return results
    
    