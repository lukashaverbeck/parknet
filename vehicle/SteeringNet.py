# This file provides the code necessary for autonomous steering based on the vehicle's image input.
# It includes the training, evaluating and predicting process for neural net.

import os
import math
import random
import datetime
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
from PIL import Image

INPUT_SHAPE = (120, 200, 3)


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
        checkpoint_callback = ModelCheckpoint("./checkpoints/checkpoint-{epoch:03d}.h5", verbose=0)

        optimizer = tf.optimizers.Adam(lr)
        data_generator = generate_data(root_directory, csv_file_train, batch_size, True)
        self.model.compile(loss=self.loss, optimizer=optimizer, batch_size=batch_size)
        history = self.model.fit_generator(data_generator, steps_per_epoch=math.ceil(num_samples_train / batch_size), epochs=epochs, validation_data=validation_data, validation_steps=validation_steps, callbacks=[tensorboard_callback, checkpoint_callback], verbose=verbose)

        return history.history

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

    def test(self, num_samples, root_directory, csv_file):
        """ determines the average deviation of the steering data given a test data set

            Args:
                samples (int): number of samples used for evaluation
                root_directory (str): path to the folder containing the evaluation data
                csv_file (str): path to the csv file mapping images to steering angles and velocities
                batch_size (int): number of samples per batch

            Returns:
                float: average deviation of the predicted steering angle from the real value
        """

        data_generator = generate_data(root_directory, csv_file, 1, False)
        steps = 0
        absolute_deviation = 0.0
        absolute_target = 0.0

        for inputs, target in data_generator:
            prediction = self.model.predict(inputs, batch_size)[0][0]
            target = target[0]

            absolute_deviation += abs(target - prediction)
            absolute_target += abs(target)
            steps += 1

            if steps >= num_samples:
                break

        absolute_deviation /= steps
        absolute_target /= steps
        total_inaccuracy = 100 * absolute_deviation / absolute_target

        absolute_deviation = round(absolute_deviation, 5)
        total_inaccuracy = round(total_inaccuracy, 2)

        return absolute_deviation, total_inaccuracy

    def predict(self, image, current_angle):
        """ predicts a steering angle based on the current image input and the current steering angle

            Args:
                image (str or numpy.ndarray): absolute path to the image or array representing the image's pixels
                current_angle (float): the vehicle's current steering angle

            Returns:
                float: predicted steering angle
        """

        if isinstance(image, str):
            image = load_image(image)
        image, current_angle, _ = prepare_data(image, current_angle)

        image = np.array([image])
        current_angle = np.array([current_angle])

        inputs = {"image": image, "previous_angle": current_angle}
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

            self.conv1 = tf.keras.layers.Conv2D(24, (5, 5), activation="elu", input_shape=INPUT_SHAPE)
            self.conv2 = tf.keras.layers.Conv2D(36, (5, 5), activation="elu")
            self.conv3 = tf.keras.layers.Conv2D(48, (3, 3), activation="elu")
            self.conv4 = tf.keras.layers.Conv2D(64, (3, 3), activation="elu")
            self.conv5 = tf.keras.layers.Conv2D(64, (3, 3), activation="elu")
            self.pool1 = tf.keras.layers.MaxPool2D((2, 2))

            self.flat1 = tf.keras.layers.Flatten()
            self.drop1 = tf.keras.layers.Dropout(0.2)

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
            previous_angle = inputs["previous_angle"]

            x = self.conv1(x)
            x = self.pool1(x)
            x = self.conv2(x)
            x = self.pool1(x)
            x = self.conv3(x)
            x = self.pool1(x)
            x = self.conv4(x)
            x = self.conv5(x)

            x = self.flat1(x)
            x = self.drop1(x)
            x = tf.concat([x, previous_angle], 1)

            x = self.flcn1(x)
            x = self.flcn2(x)
            x = self.drop1(x)
            x = self.flcn3(x)
            x = self.flcn4(x)

            return x


def load_image(path):
    """ loads an image from disk and creates a yuv numpy representation of it

        Args:
            path (str): path to the image

        Returns:
            np.ndarray: numpy representation of the yuv image
    """

    img = Image.open(path)
    img.load()
    np_array = np.asarray(img, dtype=np.uint8)  # image to array

    return np_array


def prepare_data(image, previous_angle, is_training=False, angle=None):
    """ prepares the data by augmenting and normalizing the image and angle data

        Args:
            image (np.ndarray): numpy array representing the yuv pixel values of the image
            previous_angle (float): "current" steering angle
            is_training (bool): determines whether data is prepared for training or not
            angle (float or None): angle that is to be predicted in training mode - otherwhise None

        Returns:
            np.ndarray: numpy array representing the image
            float: "current" steering angle
            float or None: angle that is to be predicted in training mode - otherwhise None
    """

    # augment data for training
    if is_training:
        # slightly change old angle
        previous_angle *= random.uniform(random.uniform(0.9, 1.0), random.uniform(1.0, 1.1))

        if random.random() > 0.5:
            # flip the image and the according steering angle
            image = np.fliplr(image)
            previous_angle *= -1

            if angle is not None:
                angle *= -1

    # crop the center of the image
    corner_x = int((image.shape[1] - INPUT_SHAPE[1]) / 2)
    corner_y = int((image.shape[0] - INPUT_SHAPE[0]) / 2)
    image = image[corner_y : corner_y + INPUT_SHAPE[0], corner_x : corner_x + INPUT_SHAPE[1]]

    image = image / 127.5 - 1  # normalize pixel values to [-1;1]

    return image, previous_angle, angle


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
    batch_previous_angle = []

    data_frame = pd.read_csv(csv_file)

    while True:
        data_frame = data_frame.sample(frac=1).reset_index(drop=True)
        
        for image_name, angle, previous_angle in zip(data_frame["image"], data_frame["angle"], data_frame["previous_angle"]):
            image = root_directory + image_name
            image = load_image(image)
            image, previous_angle, angle = prepare_data(image, previous_angle, is_training, angle)

            batch_image.append(image)
            batch_angle.append(angle)
            batch_previous_angle.append(previous_angle)

            if len(batch_image) == batch_size:
                inputs = {"image": np.array(batch_image), "previous_angle": np.array(batch_previous_angle)}
                target = np.array(batch_angle)

                yield (inputs, target)

                batch_image = []
                batch_angle = []
                batch_previous_angle = []


# train the model if the module is called directly
if __name__ == "__main__":
    num_train = 42000
    directory = "./data/nvidia-dataset-1/images/"
    csv_train = "./data/nvidia-dataset-1/train.csv"
    num_val =  3406
    csv_val = "./data/nvidia-dataset-1/test.csv"
    epochs = 10
    batch_size = 128
    learning_rate = 0.001

    net = SteeringNet()
    net.train(num_train, directory, csv_train, num_val, csv_val, epochs, batch_size, learning_rate)
