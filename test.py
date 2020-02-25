#
    # import tensorflow as tf
    # from tensorflow import keras
    # from tensorflow.keras import Model, Input, layers

    # inputs = Input(shape=(512,), name='input')
    # x = layers.Dense(64, activation='relu', name='dense_1')(inputs)
    # x = layers.Dense(64, activation='relu', name='dense_2')(x)
    # outputs = layers.Dense(3, activation='softmax', name='predictions')(x)

    # model = Model(inputs=inputs, outputs=outputs, name='medium layer')
    # model.compile(
    #     optimizer='adam', metrics=['accuracy'],
    #     loss='sparse_categorical_crossentropy'
    #     )
    # model.save(r'Machine Learning\Master\medium.h5')

import mysql.connector as sql

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor(buffered=True)

ALTER = """ALTER TABLE `userdata`.`imagedata` 
CHANGE COLUMN `rating` `rating` VARCHAR(14) NULL DEFAULT 'safe' ;"""
CURSOR.execute(ALTER)
DATAB.commit()
print('Done')