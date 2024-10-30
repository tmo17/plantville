import json
from datetime import datetime
from plant_obj import PlantObj, Nutrient  # Ensure these are imported correctly

def read_plants_from_json(file_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        plant_data = json.load(file)
    
    # Create a list of PlantObj instances
    plant_objs = []
    for plant in plant_data:
        # Create a new PlantObj instance
        plant_obj = PlantObj(
            plant_id=plant["plantID"],
            plant_type=plant["type"],
            plant_date=datetime.strptime(plant["plantDate"], "%d/%m/%Y"),  # Convert string to datetime
            roi=plant["ROI"]
        )

        # Handle optional fields if they exist
        if "roi_x" in plant:
            plant_obj._roi_x = plant["roi_x"]
        if "roi_y" in plant:
            plant_obj._roi_y = plant["roi_y"]
        
        # Extract and add nutrient data
        for key, value in plant.items():
            if '_' in key:  # Check if the key belongs to a nutrient
                nutrient_name, nutrient_prop = key.split('_', 1)
                # Find existing nutrient or create a new one if not found
                nutrient = next((n for n in plant_obj._nutrients if n.name == nutrient_name), None)
                if nutrient is None:
                    nutrient = Nutrient(nutrient_name, None, None, None)
                    plant_obj.add_nutrient(nutrient)
                setattr(nutrient, nutrient_prop, value)
        
        plant_objs.append(plant_obj)
    
    return plant_objs

# Usage example:
file_path = 'init_plants.json'
plants = read_plants_from_json(file_path)

for plant in plants:
    print(plant)