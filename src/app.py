from flask import (Flask,render_template,
                   send_from_directory, request, Response)
from dotenv import load_dotenv
import os
from farm_control import FarmControl
from database_manager import DatabaseManager
import time
import cv2


# The name map should be a flexible value instantiated when we want tocreate a new tracking class

name_map = {
    "ROI0": "Basil 1_2",
    "ROI1": "Basil 1_2",
    "ROI2": "Basil 1_3",
    "ROI3": "China Aster 1_1",
    "ROI4": "China Aster 1_2",
    "ROI5": "China Aster 1_3",
    "ROI6": "Basil 2_1",
    "ROI7": "Basil 2_2",
    "ROI8": "Basil 2_3",
    "ROI9": "China Aster 2_1",
    "ROI10": "China Aster 2_2",
    "ROI11": "China Aster 2_3"
}

def create_app():
        
    load_dotenv()
    app = Flask(__name__, static_url_path='', static_folder='static')
    farm_control = None
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for development
    
    # Initialize farm_control here and store it in app's config or globally
    farm_control = init_farm_control()
    app.config['farm_control'] = farm_control  # Ensures main is called within the app context

    # Register routes
    register_routes(app,farm_control)

    return app

def init_farm_control():
    print("Initializing farm control")
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    db = DatabaseManager(server, database, username, password)
    farm_control = FarmControl(db)
    farm_control.startup()
    return farm_control

def gen_frames(crop_manager):
    """Generator to capture frame data with ROIs and format it for HTTP streaming."""
    while True:
        frame = crop_manager.get_image()  # Get the processed frame
        if frame is not None:
            # Encode frame to JPEG before sending it
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        else:
            time.sleep(0.01)  # Sleep briefly to wait for the next frame




def register_routes(app,farm_control):
    @app.route('/greenness_history')
    def greenness_history():
        pass




    @app.route('/algorithms')
    def algorithms():
        return render_template('algorithms.html')
    



    @app.route('/greenness')
    def greenness():
        pass
        # return jsonify({'latest_greenness': 1})


    @app.route('/video_feed')
    def video_feed():
        """Route to stream video with ROIs from the camera."""
        crop_id = request.args.get('cropId', default='1', type=str)
        crop_manager = farm_control.get_crop_manager(crop_id)
        return Response(gen_frames(crop_manager),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/')
    def index():
        # Pass the CropID to the template
        return render_template('index.html', crop_id='staticCropId',greenness=None)


    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory('static', filename)
    

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', debug=True, threaded=True)