import argparse

parser = argparse.ArgumentParser(
    prog='Machine Learning', 
    description='Command line interface for common ML operations and projects'
    )
parser.add_argument(
    '-n', '--num', type=int,
    help='Number of streams', default=2
    )
args = parser.parse_args()

from . import *
from .dataset import Custom_Dataset
from .. import EPOCH, np

import matplotlib.pyplot as plt

print(tf.__version__)

data = Custom_Dataset('Medium')
train_ds, test_ds = data.load_data()

image_batch, label_batch = next(iter(train_ds))

plt.figure(figsize=(10, 10))

for i in range(9):

    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(image_batch[i].numpy().astype("uint8"))
    label = label_batch[i]
    plt.title(data.class_names[label])
    plt.axis("off")

model = tf.keras.Sequential([
    tf.keras.layers.experimental.preprocessing.Rescaling(1./255),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10)
    ])
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
    )
model.fit(train_ds, validation_data=test_ds, epochs=EPOCH)
test_loss, test_acc = model.evaluate(test_ds, verbose=2)