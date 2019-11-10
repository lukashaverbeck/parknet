# This file provides the code necessary for autonomous driving based on the vehicle's image input.
# It includes the training, evaluating and predicting process for the according neural net.
#
# author: @lukashaverbeck
# version: 1.1 (10.11.2019)
#
# TODO add functionality for setting chechpoints while training

import os
import math
import random
import datetime
import subprocess
import numpy as np
import tensorflow as tf
from skimage.io import imread


class SteeringNet:
    """ covers the deep learning model by providing high level functionality for training, evaluating and predictions of
        a deep learning model for autonomous driving
    """

    LOSS_WEIGHTS = [100.0, 0]

    def __init__(self):
        self.model = self.Model()
        self.loss = "mean_squared_error"

    def train(self, num_samples_train, root_directory, csv_file_train, num_samples_validation=None, csv_file_validation=None, epochs=10, batch_size=64, lr=0.001, verbose=1):
        """ trains the deep learning model

            Args:
                num_samples (int): number of samples used for training
                root_directory (str): path to the folder containing the training data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                epochs (int): number of training iterations over the whole data set
                batch_size (int): number of samples per batch
                lr (float): learning rate
                verbose (int): logging verbosity level
        """

        validation_data = None
        validation_steps = None
        if csv_file_validation and num_samples_validation:
            validation_data = generate_data(root_directory, csv_file_validation, batch_size)
            validation_steps = math.ceil(num_samples_validation / batch_size)

        log_dir = os.path.join("logs", "fit", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

        optimizer = tf.optimizers.Adam(lr)
        data_generator = generate_data(root_directory, csv_file_train, batch_size)
        self.model.compile(loss=self.loss, loss_weights=self.LOSS_WEIGHTS, optimizer=optimizer, batch_size=batch_size)
        self.model.fit_generator(data_generator, steps_per_epoch=math.ceil(num_samples_train / batch_size), epochs=epochs, validation_data=validation_data, validation_steps=validation_steps, callbacks=[tensorboard_callback], verbose=verbose)

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
        self.model.fit_generator(data_generator, steps_per_epoch=math.ceil(num_samples / batch_size))

    def test(self, num_samples, root_directory, csv_file, batch_size=64):
        """ determines the average deviation of the steering data given a test data set

            Args:
                samples (int): number of samples used for evaluation
                root_directory (str): path to the folder containing the evaluation data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                batch_size (int): number of samples per batch

            Returns:
                float, float: average deviations of the predicted angle and velocity from the real steering values
        """

        data_generator = generate_data(root_directory, csv_file, batch_size)
        steps = 0
        deviation_angle = 0.0
        deviation_velocity = 0.0

        for inputs, target in data_generator:
            prediction = self.model.predict(inputs, batch_size)
            prediction_angle = prediction[0]
            prediction_velocity = prediction[1]

            target_angle = target[0]
            target_velocity = target[1]

            deviation_angle += np.mean(abs(abs(prediction_angle) - abs(target_angle)))
            deviation_velocity += np.mean(abs(abs(prediction_velocity) - abs(target_velocity)))
            steps += 1

            if steps * batch_size >= num_samples:
                break

        deviation_angle /= steps
        deviation_velocity /= steps

        print("average deviation steering angle:", round(deviation_angle, 2))
        print("average deviation velocity:", round(deviation_velocity, 2))

        return deviation_angle, deviation_velocity

    def predict(self, image_path, current_angle, current_velocity):
        """ predicts a steering angle and a velocity based on the current image input and driving behaviour

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

    def save(self, model_name):
        """ saves the weights of the model to disk

            Args:
                model_name (str): name of the file storing the weights
        """

        self.model.save_weights("./models/" + model_name + ".h5", save_format="h5")

    def load(self, model_path, root_directory, csv_file):
        """ loads an existing model from weights after training it on a single sample in order for the model to be built properly

            Args:
                model_path (str): path to a .h5 representation of the model's weights
                root_directory (str): path to the folder containing the evaluation data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
        """

        self.train(1, root_directory, csv_file, epochs=1, batch_size=1, lr=0.0, verbose=0)
        self.model.load_weights(model_path)

    class Model(tf.keras.Model):
        """ deep learning model for predicting the steering angle and velocity for autonomous driving """

        def __init__(self):
            """ initializes the model by defining its layers """

            super().__init__()

            self.conv1 = tf.keras.layers.Conv2D(3, (5, 5), activation="elu")
            self.conv1 = tf.keras.layers.Conv2D(16, (5, 5), activation="elu")
            self.conv2 = tf.keras.layers.Conv2D(32, (3, 3), activation="elu")
            self.conv3 = tf.keras.layers.Conv2D(48, (3, 3), activation="elu")

            self.pool1 = tf.keras.layers.MaxPool2D((3, 3))
            self.flat1 = tf.keras.layers.Flatten()
            self.drop1 = tf.keras.layers.Dropout(0.3)

            self.flcn1 = tf.keras.layers.Dense(1024, activation="elu")
            self.flcn2 = tf.keras.layers.Dense(512, activation="elu")
            self.flcn3 = tf.keras.layers.Dense(256, activation="elu")
            self.flcn4 = tf.keras.layers.Dense(128, activation="elu")
            self.flcn5 = tf.keras.layers.Dense(64)
            self.flcn6 = tf.keras.layers.Dense(2)

            self.convolutional_layers = [self.conv1, self.conv2, self.conv3]
            self.dense_layers = [self.flcn1, self.flcn2, self.flcn3, self.flcn4, self.flcn5, self.flcn6]

        def call(self, inputs):
            """ propagates forward through the neural net

                Args:
                    inputs (dict): list of numpy arrays containing the input batches (images, angles, velocities)
            """

            x = inputs["image"]
            old_angle = inputs["old_angle"]
            old_velocity = inputs["old_velocity"]

            for convolution in self.convolutional_layers:
                x = convolution(x)
                x = self.pool1(x)
                x = self.drop1(x)

            x = self.flat1(x)
            x = tf.concat([x, old_angle, old_velocity], 1)

            for dense in self.dense_layers:
                x = self.drop1(x)
                x = dense(x)

            angles = x[:, 0]
            velocities = x[:, 1]

            return angles, velocities


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

        TODO substitute randomly generated old steering values by real angles
    """

    batch_image = []
    batch_angle = []
    batch_velocity = []
    batch_old_angle = []
    batch_old_velocity = []

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
                batch_angle.append(angle)

                velocity = float(cells[4])
                old_velocity = velocity * random.uniform(0.90, 1.1)
                batch_velocity.append(velocity)

                batch_image.append(image)
                batch_old_angle.append(old_angle)
                batch_old_velocity.append(old_velocity)

                if len(batch_image) == batch_size:
                    inputs = {"image": np.array(batch_image), "old_angle": np.array(batch_old_angle), "old_velocity": np.array(batch_old_velocity)}
                    target = [np.array(batch_angle), np.array(batch_velocity)]

                    yield (inputs, target)

                    batch_image = []
                    batch_angle = []
                    batch_velocity = []
                    batch_old_angle = []
                    batch_old_velocity = []
