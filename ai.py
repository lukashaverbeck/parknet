# This module contains entities that provide the necessary functionality for the behaviour of a
# vehicle in complex situations that cannot be described by a set of simple rules.
# Therefore it defines a neural that takes in an image and the current steering angle
# and predicts a new steering angle for autnonomous driving under various traffic conditions.
# It also implements necessary utility functions (e.g. data preparation, augmentation, training,
# testing etc.)
#
# author: @lukashaverbeck
# version: 2.0 (31.12.2019)
# 
# TODO midterm motion planning
# TODO image segmentation for identifying pedestrians, traffic signs, traffic lights etc.

import os
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.layers as layers
import constants as const
from datetime import datetime
from tensorflow.keras.callbacks import ModelCheckpoint

assert os.path.isdir(const.Storage.CHECKPOINTS), "required checkpoint directory missing"

KEY_IMG = "image"
KEY_ANGLE = "angle"
KEY_PREVIOUS = "previous_angle"


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
    noise = np.random.randint(6, size=image.shape) - np.random.randint(6, size=image.shape)
    image = image + noise

    return image


class SteeringData:
    """ wrapper class for data used for trainign the `SteeringModel` """

    INPUT_SHAPE = (100, 200, 3)

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

    def __iter__(self):
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
        
        return np.random.uniform(0.75, 1.25) * previous_angle

    @staticmethod
    def prepare_data(image, previous_angle, angle=None, is_training=False):
        """ prepares data for training and testing
        
            Args:
                image (numpy.ndarray): numpy representation of an image
                previous_angle (float): input angle
                angle (float): target angle
                is_training (bool): boolean whether data is used for training (augment data in this case)
        """

        image = center_crop_image(image, SteeringData.INPUT_SHAPE)  # extract center
        image = image / 127.5 - 1  # normalize pixel values

        if is_training:  # augment data i training mode
            image = add_noise_to_image(image)
            image, previous_angle, angle = SteeringData.random_mirror_image(image, previous_angle, angle)
            image = shift_image(image, 10, 5)
            previous_angle = SteeringData.alter_previous_angle(previous_angle)

        # round angle values
        previous_angle = round(previous_angle, 2)
        if angle is not None: angle = round(angle, 2)

        return image, previous_angle, angle


class SteeringModel(keras.Model):
    """ deep learning model predicting steering angles based on an image input and the current steering angle
        NOTE this model is based on the architecture proposed by NVIDIA researchers for autnonomous driving
    """

    INPUT_SHAPE = (100, 200, 3)

    def __init__(self):
        """ initializes the model by defining its layers """

        super().__init__()

        # convolution layers and pooling layer
        self.conv1 = layers.Conv2D(filters=24, kernel_size=(5, 5), activation="elu")
        self.conv2 = layers.Conv2D(filters=36, kernel_size=(5, 5), activation="elu")
        self.conv3 = layers.Conv2D(filters=48, kernel_size=(5, 5), activation="elu")
        self.conv4 = layers.Conv2D(filters=64, kernel_size=(3, 3), activation="elu")
        self.conv5 = layers.Conv2D(filters=64, kernel_size=(3, 3), activation="elu")
        self.pool1 = layers.MaxPool2D(pool_size=(2, 2))

        self.flat1 = layers.Flatten()
        self.drop1 = tf.keras.layers.Dropout(0.2)

        # fully connected layers
        self.flcn1 = layers.Dense(units=100, activation="elu")
        self.flcn2 = layers.Dense(units=50, activation="elu")
        self.flcn3 = layers.Dense(units=10, activation="elu")
        self.flcn4 = layers.Dense(units=1, activation="linear")

    def __repr__(self):
        try:
            print(self.summary())
        except ValueError:
            self.predict({
                KEY_IMG: np.array([np.zeros(self.INPUT_SHAPE)]),
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

        # convolution and pooling
        x = self.conv1(images)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool1(x)
        x = self.conv3(x)
        x = self.pool1(x)
        x = self.conv4(x)
        x = self.pool1(x)
        x = self.conv5(x)

        # flatten and add current steering angle
        x = self.flat1(x)
        x = self.drop1(x)
        x = tf.concat([x, angles], 1)

        # fully connected
        x = self.flcn1(x)
        x = self.flcn2(x)
        x = self.drop1(x)
        x = self.flcn3(x)
        x = self.flcn4(x)

        return x


class SteeringNet:
    """ wrapper class simlifying accessing the `SteeringModel` """    
    
    INPUT_SHAPE = (100, 200, 3)
    BATCH_SIZE = 128
    LOSS_FUNCTION = "mean_absolute_error"
    LEARNING_RATE = 0.001
    OPTIMIZER = keras.optimizers.Adam(learning_rate=LEARNING_RATE)

    def __init__(self):
        """ initializes the model """

        self.model = SteeringModel()

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

        self.predict(np.zeros(self.INPUT_SHAPE), 0.0)
        self.model.load_weights(model_path)

    def train(self, image_directory, samples_train, csv_train, samples_val, csv_val, epochs):
        """ trains the deep learning model

            Args:
                image_directory (str): path to the directory containing the images
                samples_train (int): number of samples used for training
                csv_train (str): path to the csv file mapping training images to steering angles and velocities
                samples_val (int): number of samples used for validation
                csv_val (str): path to the csv file mapping validation images to steering angles and velocities
                epochs (int): number of training iterations over the whole data set

            Returns:
                keras.callbacks.History: training history providing information about the training progress
        """

        train_id = datetime.now().strftime("%d-%m-%y-%M-%S")

        # get training data
        train_data = SteeringData(image_directory, csv_train, self.BATCH_SIZE, True).__iter__()
        train_steps = samples_train // self.BATCH_SIZE

        # get validation data if
        validation_data = SteeringData(image_directory, csv_val, self.BATCH_SIZE, False).__iter__()
        validation_steps = samples_val // self.BATCH_SIZE

        # define callbacks
        checkpoint = ModelCheckpoint(const.Storage.CHECKPOINTS + "/" + train_id + "-{epoch:03d}.h5", verbose=1)

        # compile and train the model
        self.model.compile(loss=self.LOSS_FUNCTION, optimizer=self.OPTIMIZER, batch_size=self.BATCH_SIZE)
        history = self.model.fit_generator(
            generator=train_data,
            steps_per_epoch=train_steps,
            epochs=epochs,
            callbacks=[checkpoint], 
            validation_data=validation_data,
            validation_steps=validation_steps,
            verbose=1
        )

        return history

    def evaluate(self, img_directory, samples, csv):
        """ measures the inaccuracy of the model

            Args:
                img_directory (str): path to the directory containing the images
                samples (int): number of samples to use for the evaluation
                csv (str): path to the csv file containing the data points

            Returns:
                float: mean absolute deviation
                float: proportion between the mean absolute deviation and the average target angle
        """

        data = SteeringData(img_directory, csv, 1, False)  # get evaluation data

        average_target = 0.0
        absolute_deviation = 0.0
        absolute_steps = 0

        # iterate over evaluation dataa
        for inputs, target in data:
            # get input and target values
            image = inputs[KEY_IMG][0]
            previous_angle = inputs[KEY_PREVIOUS][0]
            target = target[0]
            
            # get prediction and calculate the deviation
            prediction = self.predict(image, previous_angle)
            average_target += abs(target)
            absolute_deviation += abs(prediction - target)
            absolute_steps += 1

            if absolute_steps >= samples: break

        # calculate average
        average_target /= absolute_steps
        absolute_deviation /= absolute_steps

        relative_deviation = absolute_deviation / average_target  # calculate proportion
        
        # print evaluation results
        print(f"absolute deviation of {round(absolute_deviation, 2)}°")
        print(f"relative deviation of {100 * round(relative_deviation, 4)}%")

        return absolute_deviation, relative_deviation


assert SteeringData.INPUT_SHAPE == SteeringNet.INPUT_SHAPE == SteeringModel.INPUT_SHAPE, "steering input shape must be consistent"

if __name__ == "__main__":
    net = SteeringNet()
    net.train(
        image_directory = "./data/nvidia-dataset-1/images/",
        samples_train = 42000, 
        csv_train = "./data/nvidia-dataset-1/train.csv",
        samples_val = 3406,
        csv_val = "./data/nvidia-dataset-1/test.csv",
        epochs = 5
    )
