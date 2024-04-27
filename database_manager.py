import pymssql
import json

class DatabaseManager:
    def __init__(self, server, database, username, password):
        self.connection = pymssql.connect(server=server, user=username, password=password, database=database)
        self.cursor = self.connection.cursor()

    def initialize(self):
        pass

    def delete(self, table_name):
        self.cursor.execute(f"DELETE FROM {table_name}")
        self.connection.commit()
    
    def create_table(self):
        self.cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CurrentPlants]') AND type in (N'U'))
        CREATE TABLE CurrentPlants (
            PlantID VARCHAR(50) PRIMARY KEY,
            Type VARCHAR(50),
            PlantDate DATE,
            SoilType VARCHAR(50),
            ROI INT,
            LightType VARCHAR(50),
            WaterType VARCHAR(50),
            WaterFrequency VARCHAR(50),
            WaterAmount VARCHAR(50)
        )
        """)
        self.connection.commit()

    def drop_table(self, table_name):
        try:
            self.cursor.execute(f"DROP TABLE {table_name}")
            self.connection.commit()
            print(f"Table {table_name} dropped successfully.")
        except pymssql.DatabaseError as e:
            print(f"An error occurred when dropping table {table_name}: {e}")

    def get_current_crops(self):
        self.cursor.execute("SELECT CropId, TimePlanted FROM CurrentCrops")
        return self.cursor.fetchall()

    def add_crop(self, cropId, time):
        self.cursor.execute("""
            INSERT INTO CurrentCrops (CropId, TimePlanted)
            VALUES (%s, %s)
        """, (cropId, time))
        self.connection.commit()

    def store_image_data(self, plant_id, time, image):
        self.cursor.execute("""
            INSERT INTO ImageData (PlantID, Time, Image)
            VALUES (%s, %s, %s)
        """, (plant_id, time, image))
        self.connection.commit()

    def get_current_plants(self):
        """ Fetch all current plant entries from the database. """
        self.cursor.execute("SELECT * FROM PlantData")
        return self.cursor.fetchall()
    
    def get_plant_ids_from_crop(self, crop_id):
        with self.connection.cursor(as_dict=True) as cursor:
            query = "SELECT PlantID FROM Crop WHERE CropId = %s"
            cursor.execute(query, (crop_id,))
            return [row['PlantID'] for row in cursor.fetchall()]

    def get_plant_data_from_plant_id(self, plant_id):
        with self.connection.cursor(as_dict=True) as cursor:
            query = """
            SELECT p.PlantID, p.PlantType, p.Time_Planted, pd.Log_Time, pd.ROI, pd.ROI_X, pd.ROI_Y,
                   pd.Greeness, pd.Soil_Type, pd.Light_Type, pd.Light_Frequency, pd.Light_Amount,
                   pd.Water_Type, pd.Water_Frequency, pd.Water_Amount
            FROM Plant p
            JOIN PlantData pd ON p.PlantID = pd.PlantID
            WHERE p.PlantID = %s
            """
            cursor.execute(query, (plant_id,))
            return cursor.fetchall()

    def get_plants_from_crop(self, crop_id):
        plant_ids = self.get_plant_ids_from_crop(crop_id)
        plant_data = []
        for plant_id in plant_ids:
            data = self.get_plant_data_from_plant_id(plant_id)
            plant_data.extend(data)
        return plant_data

    def add_plant(self, plant_obj):
        """Dynamically constructs SQL to insert a new plant into the Plant table."""
        base_query = "INSERT INTO Plant (PlantID, PlantType, Time_Planted"
        base_values = [plant_obj.plant_id, plant_obj.plant_type, plant_obj.plant_date]
        query_suffix = ") VALUES (%s, %s, %s"

        # Additional attributes can be added here with similar checks
        # For now, let's keep it simple with the base attributes

        # Complete and execute the query
        final_query = base_query + query_suffix + ")"
        self.cursor.execute(final_query, tuple(base_values))
        self.connection.commit()

    def add_crop_plant_association(self, crop_id, plant_id):
        """Inserts a new association between a crop and a plant into the Crop table."""
        query = "INSERT INTO Crop (CropId, PlantID) VALUES (%s, %s)"
        self.cursor.execute(query, (crop_id, plant_id))
        self.connection.commit()

    def add_plant_data(self, plant_obj):
        """ Dynamically constructs SQL to insert a new plant into the database, handling both plant properties and nutrients. """
        # Start the base query with mandatory fields
        base_query = "INSERT INTO PlantData (PlantID, Time, ROI"
        base_values = [plant_obj.plant_id, plant_obj.plant_date, plant_obj.roi]
        query_suffix = ") VALUES (%s, %s, %s"

        # Add dynamic fields for nutrients and other attributes
        if hasattr(plant_obj, 'roi_x'):  # Just an example, apply similar checks for other attributes
            base_query += ", ROI_X"
            base_values.append(plant_obj.roi_x)
            query_suffix += ", %s"

        # Add dynamic fields for nutrients and other attributes
        if hasattr(plant_obj, 'roi_y'):  # Just an example, apply similar checks for other attributes
            base_query += ", ROI_Y"
            base_values.append(plant_obj.roi_y)
            query_suffix += ", %s"

        for nutrient in plant_obj.get_nutrients():
            base_query += f", {nutrient.name}_Type, {nutrient.name}_Frequency, {nutrient.name}_Amount"
            base_values.extend([nutrient.type, nutrient.frequency, nutrient.amount])
            query_suffix += ", %s, %s, %s"

        # Complete and execute the query
        final_query = base_query + query_suffix + ")"
        self.cursor.execute(final_query, tuple(base_values))
        self.connection.commit()


    def close(self):
        self.connection.close()
