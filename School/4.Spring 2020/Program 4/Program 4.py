import csv
import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D

def preprocess():

    with open(r'School\4.Spring 2020\Program 4\ramen-ratings.csv', encoding='utf8') as csv_file:
        reviews = [line for line in csv.reader(csv_file)]
    
    companies = [review[1] for review in reviews[1:]]
    for company in set(companies):
        if companies.count(company) == 1:
            for num, review in enumerate(reviews):
                if company in review: 
                    reviews[num][1] = 'Other'
                    break
                        
    variety = [word for review in reviews[1:] for word in review[2].split()]
    variety = {word for word in variety if variety.count(word) >= 100}
    for num, review in enumerate(reviews[1:]):
        
        try: reviews[num + 1][2] = ' '.join(set(review[2].split()) & variety)
        except: pass
    
    return reviews

data = preprocess()

model = Sequential([
    Conv2D(16, 3, padding='same', activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH ,3)),
    MaxPooling2D(),
    Conv2D(32, 3, padding='same', activation='relu'),
    MaxPooling2D(),
    Conv2D(64, 3, padding='same', activation='relu'),
    MaxPooling2D(),
    Flatten(),
    Dense(512, activation='relu'),
    Dense(1)
    ])

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=['accuracy']
    )