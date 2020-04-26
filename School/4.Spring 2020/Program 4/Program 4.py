import csv
# import numpy as np
# import matplotlib.pyplot as plt

# import tensorflow as tf
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D
# from tensorflow.keras.preprocessing.image import ImageDataGenerator

def preprocess():

    with open(r'School\4.Spring 2020\Program 4\ramen-ratings.csv', encoding='utf8') as csv_file:
        reviews = [line for line in csv.reader(csv_file)]
        
    company_count = {}
    for review in reviews[1:]:
        company_count[review[1]] = company_count.get(review[1], 0) + 1
    for company, count in company_count.items():
        if count == 1:
            for num, review in enumerate(reviews):
                if company in review:
                    reviews[num][1] = 'Other'

    return reviews

data = preprocess()
