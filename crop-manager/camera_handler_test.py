import unittest
import numpy as np
import time
import cv2

from camera_handler import CameraHandler
import logging


class TestCameraHandler(unittest.TestCase):

    def setUp(self):
        # self.get_available_cameras()
        self.camera = CameraHandler()
        self.camera.start()
        

    def get_available_cameras(self):
        available_cameras = []
        # Set a reasonable maximum index for camera checks to prevent unnecessary attempts
        max_camera_index = 2 # Adjust based on the maximum number of cameras you expect
        
        for i in range(max_camera_index):
            logging.debug(f"Checking camera {i}")
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    available_cameras.append(i)
                    logging.info(f"Camera {i} is available.")
                else:
                    logging.warning(f"Camera {i} could not be opened.")
            except Exception as e:
                logging.error(f"Failed to check camera {i}: {e}")
            finally:
                cap.release()

        logging.debug(f"Available cameras: {available_cameras}")
        return available_cameras


    def test_start_stop(self):
        self.assertTrue(self.camera.running, "Camera should be running")
        self.camera.stop()
        self.assertFalse(self.camera.running, "Camera should be stopped")

    def test_is_camera_open(self):
        
        self.assertTrue(self.camera.is_camera_open(), "Camera should be open")
        self.camera.stop()
        self.assertFalse(self.camera.is_camera_open(), "Camera should be closed")

    def test_get_latest_frame(self):
        
        time.sleep(1)  # Wait for a frame to be captured
        # import pdb; pdb.set_trace()
        frame = self.camera.get_latest_frame()
        self.assertIsNotNone(frame, "Frame should not be None")
        self.assertIsInstance(frame, bytes, "Frame should be of type bytes")
        self.camera.stop()

    def test_get_camera_properties(self):
        
        width, height, fps = self.camera.get_camera_properties()
        self.assertIsNotNone(width, "Width should not be None")
        self.assertIsNotNone(height, "Height should not be None")
        self.assertIsNotNone(fps, "FPS should not be None")
        self.camera.stop()

    def test_decode_frame(self):
        time.sleep(1)  # Wait for a frame to be captured
        frame = self.camera.get_latest_frame()
        self.assertIsNotNone(frame, "Frame should not be None")
        nparr = np.frombuffer(frame, np.uint8)
        decoded_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        self.assertIsNotNone(decoded_frame, "Decoded frame should not be None")
        self.assertEqual(decoded_frame.ndim, 3, "Decoded frame should have 3 dimensions (color image)")
        self.camera.stop()

if __name__ == '__main__':
    unittest.main()