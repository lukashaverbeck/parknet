import threading


class Camera:
    def __init__(self):
        self.__last_image = None
        self.__number_of_uses = 0

    def start(self):
        if self.__number_of_uses <= 0:
            self.__number_of_uses = 1
            recorder_thread = threading.Thread(target=self.record)
            recorder_thread.start()

    def stop(self):
        self.__number_of_uses -= 1

        if self.__number_of_uses < 0:
            self.__number_of_uses = 0

    def record(self):
        pass

    # -- getters --

    def get_image(self):
        return self.__last_image