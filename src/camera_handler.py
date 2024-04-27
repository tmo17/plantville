import cv2
import threading
import queue
import time

class CameraHandler:
    """Handles camera operations for capturing and buffering video frames."""
    
    def __init__(self, camera_ind=0, target_fps=30):
        """Initialize the CameraHandler with a specific camera index and target frame rate."""
        self.camera = cv2.VideoCapture(camera_ind)
        if not self.camera.isOpened():
            raise ValueError("Unable to open video source")
        
        # Attempt to set the frame rate, if supported by the camera hardware
        self.camera.set(cv2.CAP_PROP_FPS, target_fps)
        
        # Queue to store encoded frames, limiting to 10 to avoid excessive memory use
        self.frame_queue = queue.Queue(maxsize=10)
        
        # Setting up the thread to run frame capturing in the background
        self.thread = threading.Thread(target=self.capture_frames, daemon=True)
        self.running = True

    def start(self):
        """Start the background thread that captures frames from the camera."""
        self.thread.start()
        
    def capture_frames(self):
        """Capture frames from the camera and store them in a queue."""
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                # Encode the frame into JPEG format before placing it in the queue
                encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
                if not self.frame_queue.full():
                    self.frame_queue.put(encoded_frame)
            else:
                # Minimal sleep to prevent a tight loop if the camera read fails
                time.sleep(0.01)

    def get_current_frame(self):
        """Retrieve the latest frame from the queue if available."""
        if not self.frame_queue.empty():
            return self.frame_queue.get()
        return None

    def stop(self):
        """Stop the frame capturing thread and release the camera resource."""
        self.running = False
        self.thread.join()
        if self.camera.isOpened():
            self.camera.release()

    def __del__(self):
        """Ensure resources are cleaned up when the object is destroyed."""
        self.stop()
