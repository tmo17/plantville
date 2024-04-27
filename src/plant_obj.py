from nutrient import Nutrient

class PlantObj:
    def __init__(self, plant_id, plant_type, plant_date, roi,roi_x=-1,roi_y=-1):
        self._plant_id = plant_id
        self._type = plant_type
        self._plant_date = plant_date
        self._roi = roi
        self._roi_y = roi_y
        self._roi_x = roi_x
        self.greenness = 0
        self._nutrients = []  # Stores instances of Nutrient
        self._analytics = []  # Stores instances of Analytics



    def add_nutrient(self, nutrient):
        self._nutrients.append(nutrient)

    def add_analytic(self, analytic):
        self._analytics.append(analytic)

    
    def read_vars(self, json_data):
        for key, value in json_data.items():
            if '_' in key:
                nutrient_name, nutrient_prop = key.split('_', 1)
                nutrient = next((n for n in self.nutrients if n.name == nutrient_name), None)
                if nutrient is None:
                    nutrient = Nutrient(nutrient_name, None, None, None)
                    self.nutrients.append(nutrient)
                setattr(nutrient, nutrient_prop, value)
            else:
                setattr(self, key, value)


    def remove_nutrient(self, nutrient):
        self._nutrients = [n for n in self._nutrients if n != nutrient]

    def update_nutrient(self, nutrient_name, field_name, value):
        nutrient = next((n for n in self._nutrients if n.name == nutrient_name), None)
        if nutrient:
            nutrient.update_field(field_name, value)
        else:
            raise ValueError(f"Nutrient with name {nutrient_name} not found.")
        

    def remove_analytic(self, analytic):
        self._nutrients = [n for n in self._nutrients if n != analytic]

    def update_analytic(self, analytic_name, field_name, value):
        analytic = next((n for n in self._analytics if n.name == analytic_name), None)
        if analytic:
            analytic.update_field(field_name, value)
        else:
            raise ValueError(f"analytic with name {analytic_name} not found.")
        
    def __str__(self):
        nutrients_str = ', '.join(f"{nut.name}({nut.type}, {nut.frequency}, {nut.amount})" for nut in self._nutrients)
        return (f"Plant ID: {self._plant_id}, Type: {self._type}, Plant Date: {self._plant_date}, "
                f"ROI: {self._roi}, ROI X: {self._roi_x}, ROI Y: {self._roi_y}, "
                f"Nutrients: [{nutrients_str}]")
        