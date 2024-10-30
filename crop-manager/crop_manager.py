from camera_handler import CameraHandler
from environment_handler import EnvironmentHandler
from database_manager import DatabaseManager
from roi_evaluator import SimpleROI, ROIEvaluator
from datetime import datetime
import logging
from plant_obj import PlantObj
from typing import List
from crop_analytics import CropAnalytics, Analytic
import time
import threading
import logging
import numpy as np
import cv2

# Create logger
logger = logging.getLogger('crop_manager')


class CropManagerException(Exception):
    """Base class for exceptions in CropManager."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class NoPlantsExistForCrop(CropManagerException):
    """Exception raised when no plants exist for the specified crop ID."""
    
    def __init__(self, crop_id: str):
        super().__init__(f"No plants exist for the crop ID: {crop_id}")
        self.crop_id = crop_id


class CropManager:
    def __init__(self, crop_id,database_manager: DatabaseManager,plant_objs:List[PlantObj]=[],camera_handler:CameraHandler=None,roi_evaluator:ROIEvaluator = None,environment_handler:EnvironmentHandler = None,analytics: List[Analytic] = None):
        
        # Class variables
        self.current_frame = None
        self.crop_id = crop_id
        self.plant_objs = plant_objs
        

        # Handlers for different datastreams and action crop specific handlers
        self.database_manager = database_manager
        self.camera_handler = camera_handler or CameraHandler()
        self.environment_handler = environment_handler or EnvironmentHandler()
        self.roi_evaluator = roi_evaluator or SimpleROI()
        self.crop_analyzer = CropAnalytics()

        if analytics:
            for a in analytics:
                logger.info(f"Adding analytic for: {a.name}")
                self.crop_analyzer.add_analytic(a)

        # Now here to use the database manager to pull the list of currrent

        # Check existing crop and handle plant_objs accordingly
        logging.info(f"Checking for existing plants for crop ID {self.crop_id}")
        existing_plant_ids = self.database_manager.get_plant_ids_from_crop(self.crop_id)

        if existing_plant_ids:
            # # Crop exists, handle existing and new plants
            # if plant_objs != []:
            #     # Check each provided plant_obj against existing plant IDs
            #     for plant_obj in plant_objs:
            #         if plant_obj._plant_id in existing_plant_ids:
            #             logging.warning(f"Duplicate plant ID {plant_obj._plant_id} passed; skipping.")
            #         else:
            #             # It's a new plant, add it to the database and list
            #             self.database_manager.add_plant(plant_obj)
            #             self.plant_objs.append(plant_obj)
            #             # Add each plant to the Plant table
            #             self.database_manager.add_plant(plant_obj)
            #             # Associate plant with crop in the Crop table
            #             self.database_manager.add_crop_plant_association(self.crop_id, plant_obj.plant_id)
            #             logging.info(f"New plant ID {plant_obj._plant_id} added.")
            # else:
                # No new plants provided, fetch existing plant data and create PlantObj instances
                logger.info("No new plants provided; loading existing plant data.")
                for plant_id in existing_plant_ids:
                    plant_data = self.database_manager.get_plant_time_series_data_from_plant_id(plant_id)
                    basic_data = self.database_manager.get_plant_details(plant_id=plant_id, crop_id=self.crop_id)

                    
                    if plant_data is None:
                        logging.warning(f"No time series plant data found for plant ID {plant_id}.")
                   
                    print(f"Basic data: {basic_data}")
                    if basic_data is not []:
                        try:
                            new_plant_obj = PlantObj(plant_id, basic_data[0]['TimePlanted'] , basic_data[0]['Type'] , (int(plant_id)-1), 0, 0)
                            logging.info(f"Created new plant obj for {plant_id}.")
                        except Exception as e:
                            logging.error(f"Error creating plant object for plant ID {plant_id}.")
                            raise e
                    self.plant_objs.append(new_plant_obj)
                    print(f"Existing plant ID {plant_id} loaded with data.")
        else:
            # This is a new crop, add all plant_objs to the database
            try:
                if plant_objs:
                    for plant_obj in plant_objs:
                        # Add each plant to the Plant table
                        self.database_manager.add_plant(plant_obj)
                        # Associate plant with crop in the Crop table
                        self.database_manager.add_crop_plant_association(self.crop_id, plant_obj.plant_id)
                        self.plant_objs.append(plant_obj)
                        logging.info(f"New plant ID {plant_obj._plant_id} added for new crop.")
                else:
                    logging.error("No plants passed in for crop or already exist in the DB!")
                    raise NoPlantsExistForCrop(self.crop_id)
            # Optionally handle case where no plants are provided for a new crop
            except CropManagerException as e:
                logging.error("New crop created without initial plants.")

    def initialize(self):
        self.image_logger_thread = threading.Thread(target=self.image_logger, daemon=True)
        self.data_logger_thread = threading.Thread(target=self.data_logger, daemon=True)
        logging.info("Starting threads..")
        print("Starting threads..")
        self.image_logger_thread.start()
        self.data_logger_thread.start()
        self.camera_handler.start()
        

    def add_crop_to_db(self):
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:00')
        self.database_manager.add_crop(self.crop_id,formatted_time)

    def add_plants_to_db(self):
        for plant in self.plant_objs:
            self.database_manager.add_plant(plant)

    def decode_frame(self,encoded_frame):
        # Decode the frame if it's received as a byte string
        nparr = np.frombuffer(encoded_frame, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Ensure it's decoded to a color image
        if frame is None:
            raise ValueError("Frame could not be decoded into an image.")
        return frame
    

    def get_raw_image(self):
        raw_img = self.camera_handler.get_latest_frame()
        if raw_img is not None:
            return raw_img
        return None
 
    
    def get_image(self):
        raw_img = self.get_raw_image()
        # return raw_img
        if raw_img is not None:
            try:
               
                roi_img = self.roi_evaluator.evaluate_and_visualize_rois(self.plant_objs,raw_img)
                return roi_img
            except Exception as e:
                print("Error processing the image in roi_evaluator:", e)
        return None


    def close(self):
        self.camera_handler.stop()

    def tend_plants(self):
        self.environment_handler.tend_plants()

    def update_tend_routine(self, routine_details):
        # Parse and update tend routine
        pass

    def image_logger(self):
        """ Saves an image of the crop to the database every 3 hours. """
        while True:
            frame = self.camera_handler.get_latest_frame()
            if frame is not None:
                logger.info("Logged image data.")
                # self.database_manager.store_image_data(self.crop_id, datetime.now(), frame)
            logger.info("Image logger sleeping..")
            time.sleep(10800)  # Sleep for 3 hours


    #TODO: Update this to be more flexible for the different types of analytics and use that instead
    def data_logger(self):
        """ Logs data entries periodically. """
        successful_log = False
        while True:
            if not successful_log:
                while True:
                    frame = self.camera_handler.get_latest_frame()
                    if frame is not None:
                        successful_log = True
                        break
                    else:
                        logger.info("No frame data available, retrying in 5 minutes...")
                        time.sleep(10)  # Sleep for 5 minutes

            frame = self.camera_handler.get_latest_frame()
            if frame is not None:
                rois = self.roi_evaluator.evaluate_rois(self.plant_objs, frame=frame)
                analytics = self.crop_analyzer.run_analytics(frame, rois)
                greenness_values = analytics['Greenness ratio']

                print("Greenness values", greenness_values)
                print("Plant_objs:", self.plant_objs)

                for i, plant_obj in enumerate(self.plant_objs):
                    if plant_obj._roi >= 0:
                        self.plant_objs[i]._greenness = greenness_values[i]
                        print(f"Saving plant obj: {plant_obj} with greenness of { self.plant_objs[i]._greenness}")
                        # self.database_manager.add_plant_data(plant_obj)
                        print("Logged analytics data.")
                
                print("Saving data...")
                for plant_obj in self.plant_objs:
                    print(f"Self plant obs: {plant_obj}")
                self.database_manager.store_plant_data(self.plant_objs)
                successful_log = True
            else:
                successful_log = False
                print("No frame data available for analytics... saving nothing")

            logger.info("Analytics logger sleeping..")
            time.sleep(3600)  # Log data every hour


    def list_plants(self):
        return [(plant.name, plant.plant_id) for plant in self.plant_objs]
