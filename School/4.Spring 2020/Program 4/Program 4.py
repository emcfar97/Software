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
