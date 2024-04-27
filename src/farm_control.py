from crop_manager import CropManager
from roi_evaluator import SimpleROI
from crop_analytics import GreennessAnalytic

class FarmControl:
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self.crop_managers = {}  # Dictionary to store CropManager instances by crop ID

    def startup(self,roi_ev = SimpleROI()):
        self.crops = self.database_manager.get_current_crops()
        print(f"Crop returned: {self.crops}")
        for crop in self.crops:
            crop_id = crop[0]  # Assuming the crop ID is stored under the 'CropID' key in the tuple
            print(f"Crop_id: {crop_id}")
            if crop_id not in self.crop_managers:
                greenness_analytic = GreennessAnalytic()
                analytics = [greenness_analytic]
                crop_manager = CropManager(crop_id, self.database_manager,roi_evaluator=roi_ev,analytics=analytics)
                crop_manager.initialize()
                self.crop_managers[crop_id] = crop_manager  # Store the manager in the dictionary

    def get_crop_manager(self, crop_id):
        """ Retrieve a CropManager by crop ID. """
        return self.crop_managers.get(crop_id, None)  # Return None if the crop ID is not found

    def check_table(self):
        # This method should check the table from DatabaseManager if needed
        pass
