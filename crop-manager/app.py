from flask import Flask, send_from_directory, request, jsonify, Response
from dotenv import load_dotenv
import os
from farm_control import FarmControl
from database_manager import DatabaseManager
from crop_manager import CropManager    
import time
import cv2
from flask_cors import CORS
import logging

# Configure logging to display on the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app():
    load_dotenv()
    app = Flask(__name__, static_folder='../plant-manager-server/build', static_url_path='/')
    # Get the allowed origins from environment variables
    allowed_origins = [os.environ.get('LOCAL_HOST'), os.environ.get('WEBSITE_URL')]
    allowed_origins = [origin for origin in allowed_origins if origin]  # Remove None values

    # If you want to restrict to specific origins, use this
    if allowed_origins:
        cors = CORS(app, resources={r"/*": {"origins": allowed_origins}})
    else:
        # Allow all origins if no specific origins are provided
        cors = CORS(app, resources={r"/*": {"origins": "*"}})

    print(f"Allowed origins: {allowed_origins}")

    farm_control = None
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development

    # Initialize farm_control here and store it in app's config or globally
    farm_control, db_manager = init_farm_control()
    logging.info("Farm control initialized")
    app.config['farm_control'] = farm_control 

    # Register routes
    register_routes(app, farm_control, db_manager)

    return app

def init_farm_control():
    print("Initializing farm control")
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    port = os.getenv('DB_PORT')
    db_manager = DatabaseManager(server=server, database=database, port=port, username=username, password=password)
    farm_control = FarmControl(db_manager)
    farm_control.startup()
    return farm_control, db_manager

def gen_frames(crop_manager: CropManager):
    while True:
        if crop_manager is None:
            logging.error("Crop manager is None")
        else:
            frame = crop_manager.get_image()
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ret, buffer = cv2.imencode('.jpg', frame_rgb)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            time.sleep(0.1)

def register_routes(app, farm_control: FarmControl, db_manager: DatabaseManager):
    
    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')
    
    @app.route('/api/crops/<int:crop_id>/plants/<string:plant_id>', methods=['DELETE'])
    def delete_plant(crop_id, plant_id):
        try:
            logging.info(f"Deleting plant {plant_id} from crop {crop_id}")
            if db_manager.delete_plant_from_crop(crop_id, plant_id):
                return jsonify({"message": "Plant deleted successfully"}), 200
            else:
                return jsonify({"message": "Plant not found"}), 404
        except Exception as e:
            logging.error(f"Error deleting plant: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/plant-data', methods=['GET'])
    def get_plant_data():
        logging.info("Getting plant data")
        try:
            plant_data = db_manager.fetch_plant_data()

            # Construct a list of dictionaries with the required fields
            formatted_data = [{'PlantID': plant[0], 'Log_Time': plant[1].strftime('%Y-%m-%d %H:%M:%S'), 'Greenness': plant[2]} for plant in plant_data]
            logging.info(f"Fetched plant data: {formatted_data}")
            return jsonify(formatted_data)
        except Exception as e:
            logging.error(f"Failed to fetch plant data: {e}")
            return jsonify({"error": "Failed to fetch plant data"}), 500
    
    @app.route('/api/crops', methods=['GET'])
    def get_crops():
        logging.info("Getting crops")
        try:
            crops = db_manager.get_current_crops()
            logging.info(f"Fetched crops: {crops}")
            return jsonify(crops)
        except Exception as e:
            logging.error(f"Failed to fetch crops: {e}")
            return jsonify({"error": "Failed to fetch crops"}), 500
    
    @app.route('/api/plants', methods=['GET'])
    def get_plants():
        logging.info("Getting plants")
        try:
            plants = db_manager.get_crops_and_plants()
            logging.info(f"Fetched plants: {plants}")
            return jsonify(plants)
        except Exception as e:
            logging.error(f"Failed to fetch plants: {e}")
            return jsonify({"error": "Failed to fetch plants"}), 500

    @app.route('/api/crops', methods=['POST'])
    def create_crop():
        try:
            data = request.json
            crop_id = data['cropId']
            planted_time = data['plantedTime']
            logging.info(f"Creating crop {crop_id} with planted time {planted_time}")
            db_manager.create_crop(crop_id, planted_time)
            return jsonify({'message': 'Crop created successfully'}), 201
        except KeyError as e:
            logging.error(f"Missing key: {e}")
            return jsonify({"error": f"Missing key {e.args[0]}"}), 400
        except Exception as e:
            logging.error(f"Failed to create crop: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/crops/<int:crop_id>/plants', methods=['POST'])
    def add_plant(crop_id):
        try:
            data = request.json
            plant_id = data['plantId']
            plant_type = data['plantType']
            description = data['description']
            logging.info(f"Adding plant {plant_id} to crop {crop_id}")
            if db_manager.add_plant_to_crop(crop_id, plant_id, plant_type, description):
                return jsonify({"message": "Plant added successfully"}), 201
            else:
                return jsonify({"message": "Plant already exists!"}), 201
        except KeyError as e:
            logging.error(f"Missing key: {e}")
            return jsonify({"error": f"Missing key {e.args[0]}"}), 400
        except Exception as e:
            logging.error(f"Failed to add plant: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/video_feed')
    def video_feed():
        """Route to stream video with ROIs from the camera."""
        logging.info("Getting video feed")
        crop_id = request.args.get('cropId', default='1', type=str)
        logging.info(f"Getting video feed for crop {crop_id}")
        crop_manager = farm_control.get_crop_manager(crop_id)
        return Response(gen_frames(crop_manager), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', debug=True, threaded=True)
