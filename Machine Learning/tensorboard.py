from __future__ import absolute_import, division, print_function#, unicode_literals
import datetime
import tensorflow as tf
from tensorflow import keras

def create_model():

    return keras.models.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation='softmax')
        ])

mnist = keras.datasets.mnist

(x_train, y_train),(x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = create_model()
model.compile(
    optimizer='adam', metrics=['accuracy'],
    loss='sparse_categorical_crossentropy'
    )
log_dir="logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

model.fit(
    x=x_train, y=y_train, epochs=5, 
    validation_data=(x_test, y_test), 
    callbacks=[tensorboard_callback]
    )