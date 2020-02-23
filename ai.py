# This module contains entities that provide the necessary functionality for the behaviour of a
# vehicle in complex situations that cannot be described by a set of simple rules.
# Therefore it defines a neural that takes in an image and the current steering angle
# and predicts a new steering angle for autnonomous driving under various traffic conditions.
# It also implements necessary utility functions (e.g. data preparation, augmentation, training,
# testing etc.)
#
# version: 1.0 (31.12.2019)
# 
# TODO midterm motion planning
# TODO image segmentation for identifying pedestrians, traffic signs, traffic lights etc.

import os
import json
import math
import random
from datetime import datetime
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.layers as layers
from tensorflow.keras.callbacks import ModelCheckpoint
import constants as const


KEY_IMG = "image"
KEY_ANGLE = "angle"
KEY_PREVIOUS = "previous_angle"
INPUT_SHAPE = (100, 200, 3)


def calc_steps(data_path, batch_size):
    """ calculates the number of steps per epoch
    
        Args:
            data_path (str): path to the file storing the data
            batch_size (int): number of samples being considered per iteration

        Returns:
            int: number of steps
    """

    with open(data_path, "r") as data_file:
        lines = data_file.readlines()
        num_lines = len([l for l in lines if l.strip(" \n") != ""])

    return math.ceil(num_lines / batch_size)


def save_history(history, version):
    """ saves the training progress to disk by storing it in a JSON file

        Args:
            history (keras.callbacks.History): training history providing information about the training progress
            version (int or float or string): name of the training
    """

    with open(f"./v{version}_mae.json", mode="w+") as log:
        data = [float(x) for x in history.history["mae"]]
        json.dump(data, log, ensure_ascii=True, indent=4)

    with open(f"./{version}_val_mae.json", mode="w+") as log:
        data = [float(x) for x in history.history["val_mae"]]
        json.dump(data, log, ensure_ascii=True, indent=4)


def disply_image(image):
    """ shows an image on screen as a pyplot figure

        Args:
            image numpy.ndarray: numpy representation of an image
    """

    import matplotlib.pyplot as pyplot

    pyplot.figure()
    pyplot.imshow(image)
    pyplot.show()


def load_image(image_path):
    """ creates a numpy array of an image that is being stored on disk

        Args:
            image_path (str): path to a .jpg, .jpeg or .numpy image

        Returns:
            numpy.ndarray: numpy representation of the image

        Raises:
            TypeError: when trying to load an image that is not a JPEG or NPY file
    """

    extension = image_path.split(".")[-1]
    if extension == "npy":
        image = np.load(image_path)
    elif extension in ["jpg", "jpeg"]:
        from PIL import Image

        image = Image.open(image_path)
        image.load()
        image = np.asarray(image)
    else:
        raise TypeError("Tried to load an image with an invalid extension.")

    return image


def center_crop_image(image, target_shape):
    """ cuts out a part of the center of an image

        Args:
            image (numpy.ndarray): numpy representation of the image
            target_shape (tuple): desired dimensions of the cropped image part

        Returns:
            numpy.ndarray: numpy representation of the cropped center of the image
    """

    # ensure that the image is big enough
    assert image.shape[0] >= target_shape[0], "image does not match input dimensions"
    assert image.shape[1] >= target_shape[1], "image does not match input dimensions"
    assert image.shape[2] == target_shape[2], "image does not match input dimensions"

    # calculate corner coordinates where to start cropping
    corner_x = int((image.shape[1] - target_shape[1]) / 2)
    corner_y = int((image.shape[0] - target_shape[0]) / 2)
    
    image = image[corner_y : corner_y + target_shape[0], corner_x : corner_x + target_shape[1]]  # crop image

    return image


def shift_image(image, x_max, y_max):
    """ translates the content of an image randomly in x and y direction
        NOTE overflowing pixels are relocated to the other side of the image

        Args:
            image (numpy.ndarray): numpy representation of the image
            x_max (int): maximal translation in x direction
            y_max (int): maximal translation in y direction
    """

    # determine translation expanse and direction randomly
    shift_x = int(round(random.uniform(-x_max, x_max), 0))
    shift_y = int(round(random.uniform(-y_max, y_max), 0))

    # shift image
    image = np.roll(image, shift_x, axis=1)
    image = np.roll(image, shift_y, axis=0)

    return image


def add_noise_to_image(image):
    """ adds random noise to an image

        Args:
            image (numpy.ndarray): numpy representation of the image

        Returns:
            numpy.ndarray: numpy representation of the noised image
    """

    # determine additional pixel values and apply them to the image 
    noise = np.random.randint(2, size=image.shape) - np.random.randint(2, size=image.shape)
    image = image + noise

    return image


class SteeringData:
    """ wrapper class for data used for trainign the `SteeringModel` """

    def __init__(self, image_directory, csv_path, batch_size, is_training):
        """ initializes the `SteeringData`
        
            Args:
                image_directory (str): path to the directory storing the training / testing images
                csv_path (str): path to the csv file storing the data points
                batch_size (int): number of data points considered per batch
                is_training (bool): boolean whether data is used for training (augment data in this case)
        """

        self.image_directory = image_directory
        self.csv_path = csv_path
        self.batch_size = batch_size
        self.is_training = is_training

        if self.image_directory[-1] != "/": self.image_directory += "/"

    def generate(self):
        """ continously iterates over the data points
        
            Yields:
                tuple: input and target batches 
        """

        data = pd.read_csv(self.csv_path)  # get data points from csv file
        
        while True:
            data = data.sample(frac=1)  # randomly shuffle data points

            batch_image = []
            batch_angle = []
            batch_previous_angle = []

            for image_name, previous_angle, angle in zip(data[KEY_IMG], data[KEY_PREVIOUS], data[KEY_ANGLE]):
                # prepare image, angle and previous angle
                image_path = self.image_directory + image_name
                image = load_image(image_path)
                image, angle, previous_angle = SteeringData.prepare_data(image, previous_angle, angle, self.is_training)
                
                # add data point to the corresponding batches
                batch_image.append(image)
                batch_angle.append(angle)
                batch_previous_angle.append(previous_angle)

                if len(batch_image) == self.batch_size:
                    # ensure that the data is yielded in the required format
                    target = np.array(batch_angle)
                    inputs = {
                        KEY_IMG: np.array(batch_image),
                        KEY_PREVIOUS: np.array(batch_previous_angle)
                    }

                    yield inputs, target

                    # clear batches
                    batch_image = []
                    batch_angle = []
                    batch_previous_angle = []

    @staticmethod
    def random_mirror_image(image, previous_angle, angle):
        """ flips an image and the corresponding angles with a 50% probability
        
            Args:
                image (numpy.ndarray): numpy representation of the image
                previous_angle (float): input angle
                angle (float): target angle

            Returns:
                tuple: image, input angle and target angle (might be flipped)
        """

        if random.random() < 0.5:  # mirror data in 50% of the cases
            image = np.flip(image, axis=1)
            previous_angle *= -1
            angle *= -1

        return image, previous_angle, angle

    @staticmethod
    def alter_previous_angle(previous_angle):
        """ slightly changes an angle randomly
        
            Args:
                previous_angle (float): input angle to be adjusted

            Returns:
                float: adjusted angle
        """
        
        return np.random.uniform(0.85, 1.15) * previous_angle

    @staticmethod
    def prepare_data(image, previous_angle, angle=None, is_training=False):
        """ prepares data for training and testing
        
            Args:
                image (numpy.ndarray): numpy representation of an image
                previous_angle (float): input angle
                angle (float): target angle
                is_training (bool): boolean whether data is used for training (augment data in this case)
        """

        image = center_crop_image(image, INPUT_SHAPE)  # extract center

        if is_training:  # augment data i training mode
            image = add_noise_to_image(image)
            image, previous_angle, angle = SteeringData.random_mirror_image(image, previous_angle, angle)
            image = shift_image(image, 6, 2)
            previous_angle = SteeringData.alter_previous_angle(previous_angle)

        # normalize and round angle values
        previous_angle = round(previous_angle, 5)
        if angle is not None: angle = round(angle, 5)

        image = image / 127.5 - 1  # normalize pixel values

        return image, previous_angle, angle


class SteeringModel(keras.Model):
    """ deep learning model predicting steering angles based on an image input and the current steering angle
        NOTE this model is based on the architecture proposed by NVIDIA researchers for autnonomous driving
    """

    def __init__(self):
        """ initializes the model by defining its layers """

        super().__init__()
        
        regulizer = keras.regularizers.l2(0.001)

        # convolution layers and pooling layer
        self.conv1 = layers.Conv2D(filters=24, kernel_size=(5, 5), strides=(2, 2), kernel_regularizer=regulizer, activation="elu")
        self.conv2 = layers.Conv2D(filters=36, kernel_size=(5, 5), strides=(2, 2), kernel_regularizer=regulizer, activation="elu")
        self.conv3 = layers.Conv2D(filters=48, kernel_size=(5, 5), strides=(2, 2), kernel_regularizer=regulizer, activation="elu")
        self.conv4 = layers.Conv2D(filters=64, kernel_size=(3, 3), kernel_regularizer=regulizer, activation="elu")
        self.conv5 = layers.Conv2D(filters=64, kernel_size=(3, 3), kernel_regularizer=regulizer, activation="elu")

        self.flat1 = layers.Flatten()

        # fully connected layers
        self.flcn1 = layers.Dense(units=100, kernel_regularizer=regulizer, activation="elu")
        self.flcn2 = layers.Dense(units=50, kernel_regularizer=regulizer, activation="elu")
        self.flcn3 = layers.Dense(units=10, activation="linear")
        self.flcn4 = layers.Dense(units=1, activation="linear")

    def __repr__(self):
        try:
            print(self.summary())
        except ValueError:
            self.predict({
                KEY_IMG: np.array([np.zeros(INPUT_SHAPE)]),
                KEY_PREVIOUS: np.array([0.0])
            })

            print(self.summary())
        
        return ""

    def call(self, inputs):
        """ propagates through the neural net

            Args:
                inputs (dict): dictionary providing the image and steering angle batches

            Returns:
                numpy.ndarray: numpy array containing the predicted angles
        """

        images = inputs[KEY_IMG]
        angles = inputs[KEY_PREVIOUS]

        # convolutions
        x = self.conv1(images)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.conv5(x)

        # flatten and add current steering angle
        x = self.flat1(x)
        x = tf.concat([x, angles], 1)

        # fully connected
        x = self.flcn1(x)
        x = self.flcn2(x)
        x = self.flcn3(x)
        x = self.flcn4(x)

        return x


class SteeringNet:
    """ wrapper class simlifying accessing the `SteeringModel` """    
    
    IMG_DIRECTORY = "./data/steering/images/"
    CSV_TRAIN = "./data/steering/train.csv"
    CSV_VALIDATION = "./data/steering/validation.csv"

    def __init__(self):
        """ initializes the model by loading the default weights """

        self.model = SteeringModel()
        self.load(const.Storage.DEFAULT_STEERING_MODEL)

    def __repr__(self):
        return self.model.__repr__()

    def predict(self, image, current_angle):
        """ predicts a steering angle based on the current image input and the current steering angle

            Args:
                image (str or numpy.ndarray): absolute path to the image or array representing the image's pixels
                current_angle (float): the vehicle's current steering angle

            Returns:
                float: predicted steering angle
        """

        if isinstance(image, str):  # load image if it is not a numpy array yet
            image = load_image(image)

        # ensure that the data is provided in the required format
        image, current_angle, _ = SteeringData.prepare_data(image, current_angle)
        image = np.array([image])
        current_angle = np.array([current_angle])
        inputs = {"image": image, "previous_angle": current_angle}

        angle = self.model.predict(inputs)[0][0]  # predict steering angle value
        return angle

    def load(self, model_path):
        """ loads an existing model from a weights file

            Args:
                model_path (str): path to a representation of the model's weights
        """

        self.predict(np.zeros(INPUT_SHAPE), 0.0)
        self.model.load_weights(model_path)

    def train(self, version, epochs=50, batch_size=256, loss="mae", lr=0.001, optimizer="adam"):
        """ trains the deep learning model

            Args:
                version (int or float or string): name of the training
                epochs (int): number of training iterations over the whole data set
        """

        if not os.path.isdir(const.Storage.CHECKPOINTS):
            os.mkdir(const.Storage.CHECKPOINTS)
        if not os.path.isdir(f"{const.Storage.CHECKPOINTS}/v{version}"):
            os.mkdir(f"{const.Storage.CHECKPOINTS}/v{version}")        

        # get training and validation data
        train_data = SteeringData(self.IMG_DIRECTORY, self.CSV_TRAIN, batch_size, True).generate()
        validation_data = SteeringData(self.IMG_DIRECTORY, self.CSV_VALIDATION, batch_size, False).generate()
        train_steps = calc_steps(self.CSV_TRAIN, batch_size)
        validation_steps = calc_steps(self.CSV_VALIDATION, batch_size)

        # define callbacks
        checkpoint = ModelCheckpoint(const.Storage.CHECKPOINTS + "/v" + str(version) + "/{epoch:03d}.h5", verbose=0)

        # compile and train the model
        self.model.compile(loss=loss, optimizer=optimizer, metrics = ["mae"])
        history = self.model.fit_generator(
            generator=train_data,
            steps_per_epoch=train_steps,
            epochs=epochs,
            callbacks=[checkpoint], 
            validation_data=validation_data,
            validation_steps=validation_steps,
            verbose=1
        )

        save_history(history, version)  # save training process to disk

    def evaluate(self):
        """ measures the inaccuracy of the model

            Returns:
                float: mean absolute deviation
                float: proportion between the mean absolute deviation and the average target angle
        """

        data = SteeringData(self.IMG_DIRECTORY, self.CSV_VALIDATION, 1, False)  # get evaluation data
        samples = calc_steps(self.CSV_VALIDATION, 1)

        average_target = 0.0
        absolute_deviation = 0.0
        marginal_deviation = 0
        steps = 0

        # iterate over evaluation dataa
        for inputs, target in data:
            # get input and target values 
            image = inputs[KEY_IMG][0]
            previous_angle = inputs[KEY_PREVIOUS][0]
            target = target[0]

            prediction = self.predict(image, previous_angle)
            deviation = abs(prediction - target)
            average_target += abs(target)
            absolute_deviation += deviation
            steps += 1

            if deviation < 1:
                marginal_deviation += 1

            print(f"{round(prediction, 2)} \t\t {round(target, 2)} \t\t {round(target - prediction, 2)}")

            if steps >= samples: break

        # calculate average
        average_target /= steps
        absolute_deviation /= steps

        # calculate proportion
        relative_deviation = absolute_deviation / average_target
        marginal_deviation /= steps
        
        # print evaluation results
        print(f"absolute deviation of {round(absolute_deviation, 2)}°")
        print(f"relative deviation of {100 * round(relative_deviation, 4)}%")
        print(f"{100 * round(marginal_deviation, 4)}% of the predictions deviated minimally")

        return absolute_deviation, relative_deviation, marginal_deviation


if __name__ == "__main__":
    net = SteeringNet()
    net.train(
        version=1,
        epochs=100,
        batch_size=64,
        loss="mae",
        lr=0.00075,
        optimizer="adam"
    )
