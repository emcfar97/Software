from __future__ import absolute_import, division, print_function, unicode_literals
import os, pathlib
from os.path import join, isdir
import numpy as np
import tensorflow as tf
from tensorflow import keras

root = os.getcwd()[:2].upper()
AUTOTUNE = tf.data.experimental.AUTOTUNE

def prepare_for_training(ds, cache=True, shuffle_buffer_size=1000):
    
    # This is a small dataset, only load it once, and keep it in memory.
    # use `.cache(filename)` to cache preprocessing work for datasets that don't
    # fit in memory.
    if cache:
        if isinstance(cache, str):
            ds = ds.cache(cache)
        else:
            ds = ds.cache()

    ds = ds.shuffle(buffer_size=shuffle_buffer_size)

    # Repeat forever
    ds = ds.repeat()

    ds = ds.batch(BATCH_SIZE)

    # `prefetch` lets the dataset fetch batches in the background while the model
    # is training.
    ds = ds.prefetch(buffer_size=AUTOTUNE)

    return ds

def get_label(file_path):
    
    parts = tf.strings.split(file_path, '/')
    return parts[-2] == CLASS_NAMES

def decode_img(img):
    
    img = tf.image.decode_jpeg(img, channels=3) #color images
    img = tf.image.convert_image_dtype(img, tf.float32) 
    #convert unit8 tensor to floats in the [0,1]range
    return tf.image.resize(img, [IMG_WIDTH, IMG_HEIGHT]) 

def process_path(file_path):
    
    label = get_label(file_path)
    img = tf.io.read_file(file_path)
    img = decode_img(img)
    return img, label

path = rf'{root}\Users\Emc11\Dropbox\Pictures\4.Reference\5.Machine Learning\Medium'
data_dir = pathlib.Path(path)

BATCH_SIZE = 32
IMG_HEIGHT = 128
IMG_WIDTH = 128
STEPS_PER_EPOCH = np.ceil(
    len(list(data_dir.glob('*/*.jpg'))) / BATCH_SIZE
    )

# The 1./255 is to convert from uint8 to float32 in range [0,1].
image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
CLASS_NAMES = np.array([item.name for item in data_dir.glob('*')])
train_data_gen = image_generator.flow_from_directory(
    directory=str(data_dir), batch_size=BATCH_SIZE, shuffle=True, 
    target_size=(IMG_HEIGHT, IMG_WIDTH), classes=list(CLASS_NAMES)
    )

# Set `num_parallel_calls` so multiple images are loaded/processed in parallel.
list_ds = tf.data.Dataset.list_files(str(data_dir/'*/*'))
labeled_ds = list_ds.map(process_path, num_parallel_calls=AUTOTUNE)

train_ds = prepare_for_training(labeled_ds)
train_images, train_labels = next(iter(train_ds))
show_batch(train_images.numpy(), train_labels.numpy())

# train_images, test_images = train_images / 255.0,  test_images / 255.0
#
    # options = [
    #     dir for dir in os.listdir(path)
    #     if isdir(join(path, dir))
    #     ] + ['Create new model']
    # for num, dir in enumerate(options, start=1): 
    #     print(f'{num}. {dir}')
    # else: print('x. Exit')
    # try: choice = options[int(input('Input: ')) - 1]
    # except: choice = 'x'

    # if choice in options[:-1]:
    #     model = keras.models.load_model(join(path, choice))

    # elif choice == options[-1]:  
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(28, 28)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(3, activation='softmax')
    ])
model.compile(
    optimizer='adam',metrics=['accuracy'],
    loss='sparse_categorical_crossentropy'
    )
model.fit(train_images, train_labels, epochs=6)
model.save(join(path, input('Name this model\n')), save_format='tf')
