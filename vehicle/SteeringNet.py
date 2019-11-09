# This file provides the code necessary for autonomous driving based on the vehicle's image input.
# It includes the training, evaluating and predicting process for the according neural net.
#
# author: @lukashaverbeck
# version: 1.0 (08.11.2019)
#
# TODO add velocity to the data generator
# TODO add velocity to the model

import math
import random
import numpy as np
import tensorflow as tf
from skimage.io import imread


class SteeringNet:
    """ covers the deep learning model by providing high level functionality for training, evaluating and predictions of
        a deep learning model for autonomous driving
    """

    def __init__(self):
        self.model = self.Model()
        self.loss = "mean_squared_error"

    def train(self, num_samples, root_directory, csv_file, epochs=10, batch_size=64, lr=0.001):
        """ trains the deep learning model

            Args:
                num_samples (int): number of samples used for training
                root_directory (str): path to the folder containing the training data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                epochs (int): number of training iterations over the whole data set
                batch_size (int): number of samples per batch
                lr (float): learning rate
        """

        optimizer = tf.optimizers.Adam(lr)
        data_generator = generate_data(root_directory, csv_file, batch_size)
        self.model.compile(loss=self.loss, optimizer=optimizer, batch_size=batch_size)
        self.model.fit_generator(data_generator, steps_per_epoch=math.ceil(num_samples / batch_size), epochs=epochs)

    def evaluate(self, num_samples, root_directory, csv_file, batch_size=64):
        """ evaluates the model on data the neural net was not previously trained on

            Args:
                num_samples (int): number of samples used for evaluation
                root_directory (str): path to the folder containing the evaluation data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                batch_size (int): number of samples per batch
        """

        data_generator = generate_data(root_directory, csv_file, batch_size)
        self.model.compile(loss=self.loss, batch_size=batch_size)
        self.model.fit_generator(data_generator, verbose=2, steps_per_epoch=math.ceil(num_samples / batch_size))

    def test(self, num_samples, root_directory, csv_file, batch_size=64):
        """ determines the average deviation of the steering data given a test data set

            Args:
                samples (int): number of samples used for evaluation
                root_directory (str): path to the folder containing the evaluation data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                batch_size (int): number of samples per batch

            Returns:
                float: average deviation of the predicted steering angle from the real angle

            TODO add velocity deviation
        """

        data_generator = generate_data(root_directory, csv_file, batch_size)
        steps = 0
        deviation_angle = 0

        for inputs, target in data_generator:
            prediction = self.model.predict(inputs, batch_size)
            deviation_angle += np.mean(abs(abs(prediction) - abs(target)))
            steps += 1

            if steps * batch_size >= num_samples:
                break

        deviation_angle /= steps
        print("average deviation steering angle:", round(deviation_angle, 2))

        return deviation_angle

    def predict(self, image_path, current_angle, current_velocity):
        """ predicts an steering angle and a velocity based on the current image input and driving behaviour

            Args:
                image_path (str): absolute path to the image
                current_angle (float): the vehicle's current steering angle
                current_velocity (float): the vehicle's current velocity

            Returns:
                float, float: predicted steering angle and predicted velocity
        """

        image = imread(image_path)
        image = image / 255.0
        image = np.array([image])

        current_angle = np.array([current_angle])

        inputs = {"image": image, "old_angle": current_angle}
        prediction = self.model.predict(inputs)[0]
        
        return prediction[0]

    class Model(tf.keras.Model):
        """ deep learning model for predicting the steering angle and velocity for autonomous driving

            TODO add predictions for the vehicle's velocity
        """

        def __init__(self):
            """ initializes the model by defining its layers """

            super().__init__()

            self.conv1 = tf.keras.layers.Conv2D(3, (5, 5), activation="elu")
            self.conv2 = tf.keras.layers.Conv2D(24, (5, 5), activation="elu")
            self.conv3 = tf.keras.layers.Conv2D(36, (5, 5), activation="elu")
            self.conv4 = tf.keras.layers.Conv2D(48, (5, 5), activation="elu")
            self.conv5 = tf.keras.layers.Conv2D(64, (5, 5), activation="elu")
            self.pool1 = tf.keras.layers.MaxPool2D((2, 2))

            self.flat1 = tf.keras.layers.Flatten()
            self.drop1 = tf.keras.layers.Dropout(0.4)

            self.flcn1 = tf.keras.layers.Dense(50)
            self.flcn2 = tf.keras.layers.Dense(10)
            self.flcn3 = tf.keras.layers.Dense(1)

            self.convolutional_layers = [self.conv1, self.conv2, self.conv3, self.conv4, self.conv5]
            self.dense_layers = [self.flcn1, self.flcn2, self.flcn3]

        def call(self, inputs):
            """ propagates forward through the neural net

                Args:
                    inputs (list): list of numpy arrays containing the input batches (images, angles, velocities)
            """

            x = inputs["image"]
            old_angles = inputs["old_angle"]

            for convolution in self.convolutional_layers:
                x = convolution(x)
                x = self.pool1(x)
            
            x = self.flat1(x)
            x = tf.concat([x, old_angles], 1)
            x = self.drop1(x)

            for dense in self.dense_layers:
                x = dense(x)
            
            return x


def generate_data(root_directory, csv_file, batch_size):
    """ yields steering data

        Args:
            root_directory (str): path to the folder containing the evaluation data
            csv_file (str): path to the csv file mapping image paths from the root directory to the according
                            steering angles and velocities
            batch_size (int): number of samples per batch

        Yields:
            dict, np.array: dictionary of batches with arrays for the images, the old steering angle, the old
                            velocity as well as an label with the according steering angle and velocity

        TODO add target velocity to label
        TODO substitute randomly generated old angles by real angles
        TODO add old velocities
    """

    batch_images = []
    batch_angles = []
    batch_old_angles = []

    while True:
        with open(csv_file) as log:
            line = log.readline()

            while line:
                line = log.readline()
                row = line.replace("\n", "")
                cells = row.split(",")

                if len(row) <= 0:
                    continue

                image = root_directory + cells[0]
                image = imread(image)
                image = image / 255.0
                angle = float(cells[1])
                old_angle = angle * random.uniform(0.90, 1.1)

                batch_images.append(image)
                batch_angles.append(angle)
                batch_old_angles.append(old_angle)

                if len(batch_images) == batch_size:
                    yield ({"image": np.array(batch_images), "old_angle": np.array(batch_old_angles)}, np.array(batch_angles))

                    batch_images = []
                    batch_angles = []
                    batch_old_angles = []
