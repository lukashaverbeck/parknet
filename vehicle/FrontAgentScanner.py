# allows to identify other agents

import time
import threading
import pyzbar.pyzbar as pyzbar
import picamera
import picamera.array


class FrontAgentScanner:
    """ keeps track of other agents in the camera image by scanning agent ID QR codes """

    REFRESH_INTERVAL = 1  # seconds to wait each time after refreshing the front agent ID

    def __init__(self):
        """ initializes the scanner and starts to refresh the front agent ID """

        self.__front_agent_id = None

        # start updating the front agent ID in a separate thread
        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.start()

    def refresh(self):
        """ permanently updates the front agent ID based on the current video input """

        with picamera.PiCamera() as camera:
            while True:
                with picamera.array.PiRGBArray(camera) as frame:
                    # analyze the camera input with respect to QR Codes representing an agent ID
                    camera.capture(frame, "rgb")
                    decoded_objects = pyzbar.decode(frame.array)

                    if len(decoded_objects) > 0:
                        data_bytes = decoded_objects[0].data
                        self.__front_agent_id = data_bytes.decode("utf-8")
                    else:
                        self.__front_agent_id = None

                time.sleep(self.REFRESH_INTERVAL)

    # -- getters --

    def get_front_agent_id(self):
        return self.__front_agent_id
