import numpy
import threading
import picamera
import picamera.array
from PIL import Image


def save_img_array(img_array, path):
    """ saves an given rgb image array to disk
    
        Args:
            img_array (numpy.ndarray): array representing the image's pixels
            path (str): path determining where to store the image file

        Returns:
            bool: False if None was handed as image array - otherwhise True
    """

    if img_array is None:
        return False
    
    img = Image.fromarray(img_array, "RGB")
    img.save(path)

    return True


class Camera:
    """ allows to centrally access the Pi Camera """

    def __init__(self):
        self.__last_image = None
        self.__number_of_uses = 0

    def start(self):
        """ adds a new instance accessing the camera the camera should only be accesses after this method was
            called
        """

        if self.__number_of_uses <= 0:
            self.__number_of_uses = 1
            recorder_thread = threading.Thread(target=self.record)
            recorder_thread.start()
        else:
            self.__number_of_uses += 1

    def stop(self):
        """ removes an instance from the number currently accessing instances this method should be called when the
            camera is no longer needed
        """

        self.__number_of_uses -= 1

        if self.__number_of_uses < 0:
            self.__number_of_uses = 0

    def record(self):
        """ constanly takes images as long as there is at least one instance accessing the camera """

        with picamera.PiCamera() as camera:
            camera.brightness = 60

            while self.__number_of_uses > 0:
                with picamera.array.PiRGBArray(camera) as frame:
                    camera.capture(frame, "rgb")
                    self.__last_image = frame.array

    # -- getters --

    def get_image(self):
        return self.__last_image
