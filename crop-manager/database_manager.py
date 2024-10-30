import pymssql
import json
import mysql.connector

import logging

import logging

# Configure logging to display on the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseException(Exception):
    """Custom exception class for database-related errors"""
    pass




class DatabaseManager:
    def __init__(self, username, password,server,database,port):
        self.connection = mysql.connector.connect(host=server, port= port, user=username, password=password, database=database)
        self.cursor = self.connection.cursor()
        self.check_and_create_tables()

    def initialize(self):
        pass

    def delete(self, table_name):
        self.cursor.execute(f"DELETE FROM {table_name}")
        self.connection.commit()
    
   

    def print_tables(self, table=None):
        try:
            if table is None:
                # Print the first 10 rows of each table
                print("Plant Table:")
                self.cursor.execute("SELECT * FROM Plant LIMIT 10")
                for row in self.cursor.fetchall():
                    print(row)
    
                print("\nPlantData Table:")
                self.cursor.execute("SELECT * FROM PlantData LIMIT 10")
                for row in self.cursor.fetchall():
                    print(row)
    
                print("\nCrop Table:")
                self.cursor.execute("SELECT * FROM Crop LIMIT 10")
                for row in self.cursor.fetchall():
                    print(row)
    
                print("\nImageData Table:")
                self.cursor.execute("SELECT * FROM ImageData LIMIT 10")
                for row in self.cursor.fetchall():
                    print(row)
    
                print("\nCurrentCrops Table:")
                self.cursor.execute("SELECT * FROM CurrentCrops LIMIT 10")
                for row in self.cursor.fetchall():
                    print(row)
    
            else:
                # Print the first 10 rows of the specified table
                print(f"{table} Table:")
                self.cursor.execute(f"SELECT * FROM {table} LIMIT 10")
                for row in self.cursor.fetchall():
                    print(row)
    
        except pymssql.DatabaseError as e:
            print(f"An error occurred: {e}")




    
    def check_and_create_tables(self):
        try:
            self.cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in self.cursor.fetchall()]
    
            if "Plant" not in existing_tables:
                logging.info("Plant table does not exist. Creating...")
                self.create_plant_table()
            else:
                logging.info("Plant table already exists.")
    
            if "PlantData" not in existing_tables:
                logging.info("PlantData table does not exist. Creating...")
                self.create_plant_data_table()
            else:
                logging.info("PlantData table already exists.")
    
            if "Crop" not in existing_tables:
                logging.info("Crop table does not exist. Creating...")
                self.create_crop_table()
            else:
                logging.info("Crop table already exists.")
    
            if "ImageData" not in existing_tables:
                logging.info("ImageData table does not exist. Creating...")
                self.create_image_data_table()
            else:
                logging.info("ImageData table already exists.")
    
            if "CurrentCrops" not in existing_tables:
                logging.info("CurrentCrops table does not exist. Creating...")
                self.create_current_crops_table()
            else:
                logging.info("CurrentCrops table already exists.")
    
        except mysql.connector.Error as e:
            logging.error(f"Error checking or creating tables: {e}")
            raise DatabaseException(f"Error checking or creating tables: {e}")
        
    

    def create_plant_data_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS PlantData(
            PlantID VARCHAR(50),
            Log_Time DATETIME,
            ROI INT,
            ROI_X INT,
            ROI_Y INT,
            Greenness DOUBLE,
            Soil_Type VARCHAR(50),
            Light_Type VARCHAR(50),
            Light_Frequency VARCHAR(50),
            Light_Amount VARCHAR(50),
            Water_Type VARCHAR(50),
            Water_Frequency VARCHAR(50),
            Water_Amount VARCHAR(50),
            FOREIGN KEY (PlantId) REFERENCES Plant(PlantId)
        )
        """)
        self.connection.commit()
    
    def create_plant_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Plant(
            PlantID VARCHAR(50) PRIMARY KEY,
            PlantType VARCHAR(50),
            Description VARCHAR(255)                
        )
        """)
        self.connection.commit()

    def create_crop_table(self):
        # Ensure referenced tables are created first
        self.create_plant_table()  # Assuming this method correctly creates the Plant table with PlantID as PRIMARY KEY
        self.create_current_crops_table()  # This creates CurrentCrops with CropId as PRIMARY KEY

        # Now create the Crop table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Crop(
            CropId VARCHAR(50),
            PlantID VARCHAR(50),
            PRIMARY KEY (CropId, PlantID),
            FOREIGN KEY (PlantId) REFERENCES Plant(PlantID),
            FOREIGN KEY (CropId) REFERENCES CurrentCrops(CropId)
        )
        """)
        self.connection.commit()


    def create_image_data_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ImageData (
            ImageID INT AUTO_INCREMENT PRIMARY KEY,
            CropId VARCHAR(50),
            Log_Time DATETIME,
            Image LONGBLOB,
            FOREIGN KEY (CropId) REFERENCES Crop(CropId)
        )
        """)
        self.connection.commit()

    def create_current_crops_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS CurrentCrops (
            CropId VARCHAR(50) PRIMARY KEY,
            TimePlanted DATETIME
        )
        """)
        self.connection.commit()
   
    def drop_all_tables(self):
        try:
            # Disable foreign key checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            self.connection.commit()

            # Retrieve all tables
            self.cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in self.cursor.fetchall()]

            # Drop each table
            for table in tables:
                print(f"Dropping table {table}")
                self.cursor.execute(f"DROP TABLE {table};")
                self.connection.commit()

            # Re-enable foreign key checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            self.connection.commit()
            print("All tables dropped successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            self.cursor.close()
            print("MySQL connection is closed.")

    def drop_table(self, table_name):
        try:
            self.cursor.execute(f"DROP TABLE {table_name}")
            self.connection.commit()
            print(f"Table {table_name} dropped successfully.")
        except pymssql.DatabaseError as db_err:
            print(f"An error occurred when dropping the table {table_name}: {db_err}")
        except pymssql.OperationalError as op_err:
            print(f"An unexpected error occurred when dropping the table {table_name}: {op_err}")


    def get_current_crops(self):
        try:
            # Using 'with' to ensure the cursor is closed after the block is executed
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT CropId FROM CurrentCrops")
                # Fetch all results at once
                rows = cursor.fetchall()
                # Extract the first element from each tuple to create a list of IDs
                crop_ids = [row[0] for row in rows]
                logging.info(f"Current crops: {crop_ids}")
                return crop_ids

            
        except mysql.connector.Error as e:
            logging.error(f"Database error occurred: {e}")
            return []  # Return an empty list or handle the error as appropriate
        # No need for finally to close the cursor due to the use of 'with' statement

    
    def get_crops_and_plants(self):
        try:
            with self.connection.cursor() as cursor:
                # Updated SQL to include a join with the CurrentCrops table and fetch the TimePlanted
                cursor.execute("""
                    SELECT c.CropId, p.PlantID, p.PlantType, p.Description, cc.TimePlanted
                    FROM Crop c
                    LEFT JOIN Plant p ON c.PlantID = p.PlantID
                    JOIN CurrentCrops cc ON c.CropId = cc.CropId
                """)
                results = cursor.fetchall()
                crops = {}
                for crop_id, plant_id, plant_type,description, time_planted in results:
                    if crop_id not in crops:
                        crops[crop_id] = {
                            'id': crop_id, 
                            'plants': []
                        }
                    if plant_id:
                        crops[crop_id]['plants'].append({
                            'id': plant_id,
                            'type': plant_type,
                            'plantedTime': time_planted,
                            'description':description  # Now includes the planting time
                        })
                return list(crops.values())
        except mysql.connector.Error as e:
            logging.error(f"Database error occurred: {e}")



    def create_crop(self, crop_id,time_planted):
        try:
            # Check if the crop already exists
            self.cursor.execute("SELECT 1 FROM CurrentCrops WHERE CropId = %s", (crop_id,))
            if self.cursor.fetchone():
                logging.info(f"Crop with ID {crop_id} already exists.")
            else:
                # Insert the crop since it does not exist
                self.cursor.execute("INSERT INTO CurrentCrops (CropId, TimePlanted) VALUES (%s,%s)", (crop_id,time_planted))
                self.connection.commit()
                logging.info(f"New crop with ID {crop_id} created.")
        except mysql.connector.Error as e:
            logging.error(f"Error when trying to create crop {crop_id}: {e}")
            # Consider raising an error or handling it according to your error handling policy
        finally:
            # It's good practice to ensure cursors are closed after operation
            self.cursor.close()
            # Consider re-opening the cursor if the class continues to use it after this method
            self.cursor = self.connection.cursor()



    def add_plant_to_crop(self, crop_id, plant_id, plant_type, description=""):
        # Check if the plant already exists
        self.cursor.execute("SELECT 1 FROM Plant WHERE PlantID = %s", (plant_id,))
        if self.cursor.fetchone():
            logging.info(f"Plant with ID {plant_id} already exists.")
            return False
        else:
            # Insert the new plant since it does not exist
            logging.info(f"About to acctually add plant {plant_id} to crop {crop_id}")
            try:
                self.cursor.execute("INSERT INTO Plant (PlantID, PlantType,Description) VALUES (%s, %s,%s)", (plant_id, plant_type,description))
                self.cursor.execute("INSERT INTO Crop(CropId, PlantID) VALUES (%s, %s)", (crop_id, plant_id))
            except Exception as e:
                logging.error(f"Error adding plant to crop: {e}")
                return False
            self.connection.commit()
            logging.info(f"New plant with ID {plant_id} added to crop {crop_id}.")
            return True


    def delete_plant_from_crop(self, crop_id, plant_id):
        self.cursor.execute("DELETE FROM Crop WHERE CropId = %s AND PlantID = %s", (crop_id, plant_id))
        self.cursor.execute("DELETE FROM Plant WHERE PlantID = %s", (plant_id,))
        self.connection.commit()

    def delete_crop_from_current_crops(self, crop_id):
        self.cursor.execute("DELETE FROM CurrentCrops WHERE CropId = %s", (crop_id))
        self.connection.commit()

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

    def store_plant_data(self, plant_objs):
        """
        Store multiple plant data entries into the database.
        
        Parameters:
            plant_objs (list): A list of objects, each containing data about a plant.
        """
        query = """
        INSERT INTO PlantData (
            PlantID, Log_Time, ROI, ROI_X, ROI_Y, Greeness, 
            Soil_Type, Light_Type, Light_Frequency, Light_Amount, 
            Water_Type, Water_Frequency, Water_Amount
        ) VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            # Prepare data for multiple plants
            data = []
            for plant_obj in plant_objs:
                # Extract necessary properties from plant_obj, assume greenness is defined
                # 
                print(plant_obj)
                greeness = getattr(plant_obj, 'greeness', 0)  # Default to 0 if not present
                
                # Placeholders for other attributes
                # Here you may extract these from plant_obj or define defaults
              
                roi = getattr(plant_obj, 'roi', 0)
                roi_x = getattr(plant_obj, 'roi_x', 0)
                roi_y = getattr(plant_obj, 'roi_y', 0)
                soil_type = getattr(plant_obj, 'soil_type', 'Unknown')
                light_type = getattr(plant_obj, 'light_type', 'Unknown')
                light_frequency = getattr(plant_obj, 'light_frequency', 'Unknown')
                light_amount = getattr(plant_obj, 'light_amount', 'Unknown')
                water_type = getattr(plant_obj, 'water_type', 'Unknown')
                water_frequency = getattr(plant_obj, 'water_frequency', 'Unknown')
                water_amount = getattr(plant_obj, 'water_amount', 'Unknown')

                # Append tuple to data list
                data.append((
                    plant_obj.plant_id, roi, roi_x, roi_y, greeness,
                    soil_type, light_type, light_frequency, light_amount,
                    water_type, water_frequency, water_amount
                ))

            # Execute SQL query in batch
            self.cursor.executemany(query, data)
            self.connection.commit()
            logging.info(f"Stored data for {len(plant_objs)} plants.")
        except mysql.connector.Error as e:
            logging.error(f"Database error occurred: {e}")
            raise DatabaseException(f"Database error occurred: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise DatabaseException(f"An unexpected error occurred: {e}")

    def fetch_plant_data(self):
        """Fetch plant data from the database."""
        query = """
        SELECT PlantID, Log_Time, Greeness
        FROM PlantData
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    

    def get_current_plants(self):
        """ Fetch all current plant entries from the database. """
        self.cursor.execute("SELECT CropId FROM PlantData")
        return self.cursor.fetchall()
    
    def get_plant_ids_from_crop(self, crop_id):
        with self.connection.cursor() as cursor:
            # Ensure the query is safe from SQL injection
            query = "SELECT PlantID FROM Crop WHERE CropId = %s"
            cursor.execute(query, (crop_id,))
            rows = cursor.fetchall()  # Fetch all results at once

            # Extract the first element from each tuple to create a list of IDs
            plant_ids = [row[0] for row in rows]
            logging.info(f"Plant IDs from crop {crop_id}: {plant_ids}")

            return plant_ids


    def get_plant_time_series_data_from_plant_id(self, plant_id):
        with self.connection.cursor() as cursor:
            query = """
            SELECT p.PlantID, p.PlantType, pd.Log_Time, pd.ROI, pd.ROI_X, pd.ROI_Y,
                   pd.Greeness, pd.Soil_Type, pd.Light_Type, pd.Light_Frequency, pd.Light_Amount,
                   pd.Water_Type, pd.Water_Frequency, pd.Water_Amount
            FROM Plant p
            JOIN PlantData pd ON p.PlantID = pd.PlantID
            WHERE p.PlantID = %s
            """
            cursor.execute(query, (plant_id,))
            return cursor.fetchall()
        
    def get_plant_details(self, crop_id,plant_id):
        print("Getting plant details",crop_id)
        with self.connection.cursor() as cursor:
            # The SQL query joins the Crop table with CurrentCrops and Plant to fetch the required details
            query = """
            SELECT p.PlantType, cc.TimePlanted
            FROM Crop c
            JOIN Plant p ON c.PlantID = p.PlantID
            JOIN CurrentCrops cc ON c.CropId = cc.CropId
            WHERE c.CropId = %s AND p.PlantID = %s
            """
            cursor.execute(query, (crop_id,plant_id))
            rows = cursor.fetchall()  # Fetch all results at once

            # Create a list of dictionaries based on the fetched data
            plant_details = [{'TimePlanted': row[1].strftime('%Y-%m-%d %H:%M:%S'), 'Type': row[0]} for row in rows]
            logging.info(f"Plant details from crop {crop_id}: {plant_details}")

            return plant_details

        
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
