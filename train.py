import os, pathlib, tempfile
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from Webscraping.utils import DATAB, CURSOR, execute

AUTOTUNE = tf.data.experimental.AUTOTUNE
batch_size = 32
img_height = 256
img_width = 256

def create_data(classes):

    temp_dir = tempfile.TemporaryDirectory()    
    for i in classes: os.makedirs(os.path.join(temp_dir.name, i))
    CURSOR.execute(SELECT)
    for (path, type,) in CURSOR.fetchall():
        try: 
            image = Image.open(path)
            path = os.path.join(
                temp_dir.name, classes[type], os.path.basename(path)
                )
            image.save(path)
        except: continue
    return temp_dir

ROOT = os.getcwd()[:2].upper()
SELECT = f'''(SELECT REPLACE(path, "C:", "{ROOT}"), type FROM imageData WHERE path LIKE "%jp%g" AND type=1 ORDER BY RAND() LIMIT 7500) UNION 
(SELECT REPLACE(path, "C:", "{ROOT}"), type FROM imageData WHERE path LIKE "%jp%g" AND type=0 ORDER BY RAND() LIMIT 7500)'''

classes = ['photo', 'illus']
data_dir = create_data(classes)

train_ds = keras.preprocessing.image_dataset_from_directory(
    data_dir.name,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
    )
val_ds = keras.preprocessing.image_dataset_from_directory(
    data_dir.name,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size
    )
train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# print(train_ds)
# print(train_ds.take(1))
# data_dir.cleanup()
# raise ValueError
# checkpoint_path = "Machine Learning/cp-{epoch:04d}.ckpt"
# checkpoint_dir = os.path.dirname(checkpoint_path)

# # Create a callback that saves the model's weights every 5 epochs
# cp_callback = keras.callbacks.ModelCheckpoint(
#     filepath=checkpoint_path, 
#     verbose=1, 
#     save_weights_only=True,
#     save_freq=2
#     )
# model = tf.keras.Sequential([
#     keras.layers.experimental.preprocessing.Rescaling(1./255),
#     keras.layers.Conv2D(32, 3, activation='relu'),
#     keras.layers.MaxPooling2D(),
#     keras.layers.Conv2D(32, 3, activation='relu'),
#     keras.layers.MaxPooling2D(),
#     keras.layers.Conv2D(32, 3, activation='relu'),
#     keras.layers.MaxPooling2D(),
#     keras.layers.Conv2D(32, 3, activation='relu'),
#     keras.layers.MaxPooling2D(),
#     keras.layers.Conv2D(32, 3, activation='relu'),
#     keras.layers.MaxPooling2D(),
#     keras.layers.Flatten(),
#     keras.layers.Dense(128, activation='relu'),
#     keras.layers.Dense(len(classes))
#     ])
# model.compile(
#     optimizer='adam',
#     loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
#     metrics=['accuracy']
#     )
# model.save_weights(
#     checkpoint_path.format(epoch=0)
#     )
model = keras.models.load_model(r'Machine Learning\Medium-02')
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=8,
    # callbacks=[cp_callback]
    )
model.save(r'Machine Learning\Medium-02', save_format='tf')

data_dir.cleanup()