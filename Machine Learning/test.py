from __future__ import absolute_import, division, print_function#, unicode_literals
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from os.path import join, isdir

path = 'Machine Learning'
source = r'C:\Users\Emc11\Dropbox\Pictures\4.Reference\5.Machine Learning\Medium\Medium.tgz'
class_names = [
    'Photography', 'Illustrations', '3-Dimensional'
    ]
medium_data = keras.utils.get_file(
    origin=source, fname='medium_photos', untar=True
    )
(train_images, train_labels), (test_images, test_labels) = medium_data.load_data()
train_images, test_images = train_images / 255.0,  test_images / 255.0
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
