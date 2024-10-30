import cv2
import threading
import time
import logging

class CameraHandler:
    def __init__(self, camera_index=0):
        self.camera = None
        self.camera_index = camera_index
        self.latest_frame = None  # Hold the most recent frame
        self.running = False
        self.thread = None

    def start(self):
        """Starts the camera streaming in a separate thread."""
        self.running = True
        if self.thread is None:
            # Release any previous camera instances
            self.release_camera()
            self.thread = threading.Thread(target=self.capture_frames, daemon=True)
            self.thread.start()

    def capture_frames(self):
        """Continuously capture frames from the video source."""
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            logging.error(f"Unable to open video source with index {self.camera_index}")
            self.running = False
            return

        logging.info("Starting frame capture...")
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                # Update the latest frame
                self.latest_frame = frame
            else:
                logging.warning("Failed to capture frame. Retrying...")
                time.sleep(0.1)

        logging.info("Frame capture stopped.")

    def get_latest_frame(self):
        """Returns the most recent frame captured."""
        return self.latest_frame

    def stop(self):
        """Stop the frame capturing thread and release the camera resource."""
        self.running = False
        if self.thread:
            self.thread.join()
        self.release_camera()

    def release_camera(self):
        """Release the camera resource."""
        if self.camera:
            self.camera.release()
            self.camera = None

    def __del__(self):
        """Ensure resources are cleaned up when the object is destroyed."""
        self.stop()
