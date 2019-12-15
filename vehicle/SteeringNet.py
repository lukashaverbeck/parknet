# This file provides the code necessary for autonomous steering based on the vehicle's image input.
# It includes the training, evaluating and predicting process for the according neural net.
#
# TODO add functionality for setting chechpoints while training
# TODO substitute randomly generated steering data with real data

import os
import math
import scipy
import random
import datetime
import skimage.io
import skimage.util
import skimage.color
import skimage.feature
import numpy as np
import tensorflow as tf

INPUT_SHAPE = (160, 320, 3)


class SteeringNet:
    """ covers the deep learning model by providing high level functionality for training, evaluating and predictions of
        a deep learning model for autonomous driving
    """

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
            validation_data = generate_data(root_directory, csv_file_validation, batch_size, True)
            validation_steps = math.ceil(num_samples_validation / batch_size)

        log_dir = os.path.join("logs", "fit", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

        optimizer = tf.optimizers.Adam(lr)
        data_generator = generate_data(root_directory, csv_file_train, batch_size, True)
        self.model.compile(loss=self.loss, optimizer=optimizer, batch_size=batch_size)
        self.model.fit_generator(data_generator, steps_per_epoch=math.ceil(num_samples_train / batch_size), epochs=epochs, validation_data=validation_data, validation_steps=validation_steps, callbacks=[tensorboard_callback], verbose=verbose)

    def evaluate(self, num_samples, root_directory, csv_file, batch_size=64):
        """ evaluates the model on data the neural net was not previously trained on

            Args:
                num_samples (int): number of samples used for evaluation
                root_directory (str): path to the folder containing the evaluation data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                batch_size (int): number of samples per batch
        """

        data_generator = generate_data(root_directory, csv_file, batch_size, False)
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
                float: average deviation of the predicted steering angle from the real value
        """

        data_generator = generate_data(root_directory, csv_file, batch_size, False)
        steps = 0
        deviation_angle = 0.0

        for inputs, target in data_generator:
            prediction_angle = self.model.predict(inputs, batch_size)
            target_angle = target[0]

            deviation_angle += np.mean(abs(abs(prediction_angle) - abs(target_angle)))
            steps += 1

            if steps * batch_size >= num_samples:
                break

        deviation_angle /= steps

        print("average deviation steering angle:", round(deviation_angle, 2))

        return deviation_angle

    def predict(self, image, current_angle):
        """ predicts a steering angle based on the current image input and the current steering angle

            Args:
                image (str or numpy.ndarray): absolute path to the image or array representing the image's pixels
                current_angle (float): the vehicle's current steering angle

            Returns:
                float: predicted steering angle
        """

        if isinstance(image, str):
            image = skimage.io.imread(image)
        image, current_angle = prepare_data(image, current_angle)

        image = np.array([image])
        current_angle = np.array([current_angle])

        inputs = {"image": image, "old_angle": current_angle}
        angle = self.model.predict(inputs)[0][0]
        
        return angle

    def save(self, model_name):
        """ saves the weights of the model to disk

            Args:
                model_name (str): name of the file storing the weights
        """

        self.model.save_weights("./models/" + model_name + ".h5", save_format="h5")

    def load(self, model_path):
        """ loads an existing model from weights after training it on a single sample in order for the model to be built properly

            Args:
                model_path (str): path to a .h5 representation of the model's weights
        """

        self.predict(np.zeros(INPUT_SHAPE), 0.0)
        self.model.load_weights(model_path)

    class Model(tf.keras.Model):
        """ deep learning model for predicting the steering angle and velocity for autonomous driving """

        def __init__(self):
            """ initializes the model by defining its layers """

            super().__init__()

            self.conv1 = tf.keras.layers.Conv2D(2, (5, 5))
            self.conv1 = tf.keras.layers.Conv2D(24, (5, 5))
            self.conv2 = tf.keras.layers.Conv2D(36, (5, 5))
            self.conv3 = tf.keras.layers.Conv2D(48, (3, 3))
            self.conv4 = tf.keras.layers.Conv2D(64, (3, 3))
            self.conv4 = tf.keras.layers.Conv2D(64, (3, 3))
            self.pool1 = tf.keras.layers.MaxPool2D((2, 2))

            self.flat1 = tf.keras.layers.Flatten()
            self.flcn1 = tf.keras.layers.Dense(100, activation="elu")
            self.flcn2 = tf.keras.layers.Dense(50, activation="elu")
            self.flcn3 = tf.keras.layers.Dense(10, activation="elu")
            self.flcn4 = tf.keras.layers.Dense(1)

        def call(self, inputs):
            """ propagates forward through the neural net

                Args:
                    inputs (dict): list of numpy arrays containing the input batches (images, angles)
            """

            x = inputs["image"]
            old_angle = inputs["old_angle"]

            x = self.conv1(x)
            x = self.pool1(x)
            x = self.conv2(x)
            x = self.pool1(x)
            x = self.conv3(x)
            x = self.pool1(x)
            x = self.conv4(x)

            x = self.flat1(x)
            x = tf.concat([x, old_angle], 1)

            x = self.flcn1(x)
            x = self.flcn2(x)
            x = self.flcn3(x)
            x = self.flcn4(x)

            return x


def prepare_data(image, old_angle, is_training=False):
    if is_training:
        # data augmentation: slightly change old angle
        old_angle *= random.uniform(random.uniform(0.95, 1.0), random.uniform(1.0, 1.05))

        if random.random() > 0.5:
            # data augmentation: mirror the image
            image = np.fliplr(image)
            old_angle *= -1

    image = image / 255.0

    return image, old_angle


def generate_data(root_directory, csv_file, batch_size, is_training=False):
    """ yields steering data

        Args:
            root_directory (str): path to the folder containing the evaluation data
            csv_file (str): path to the csv file mapping image paths from the root directory to the according
                            steering angles and velocities
            batch_size (int): number of samples per batch

        Yields:
            dict, np.array: dictionary of batches with arrays for the images, the old steering angle as well
                            as an label with the according steering angle and velocity

        TODO substitute randomly generated old steering values by real angles
    """

    batch_image = []
    batch_angle = []
    batch_old_angle = []

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
                image = skimage.io.imread(image)

                try:
                    angle = float(cells[1])
                    old_angle = angle

                    image, old_angle = prepare_data(image, old_angle, is_training)

                    batch_image.append(image)
                    batch_angle.append(angle)
                    batch_old_angle.append(old_angle)
                except ValueError as error:
                    continue

                if len(batch_image) == batch_size:

                    inputs = {"image": np.array(batch_image), "old_angle": np.array(batch_old_angle)}
                    target = np.array(batch_angle)

                    yield (inputs, target)

                    batch_image = []
                    batch_angle = []
                    batch_old_angle = []
