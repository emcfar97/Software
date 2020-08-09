import os, pathlib
import tensorflow as tf
from tensorflow import keras

ROOT = os.getcwd()[:2].upper()
DATA_DIR = pathlib.Path(rf'{ROOT}\Users\Emc11\Dropbox\Videos\ん')
CHECKPOINT = 'Machine Learning/Checkpoints/cp-{epoch:04d}.ckpt'
AUTOTUNE = tf.data.experimental.AUTOTUNE
MODEL_NAME = 'Medium'

EPOCHS = 1
BATCH = 32
BUFFER = 1000
IMG_COUNT = 1000
IMG_HEIGHT = 256
IMG_WIDTH = 256

def get_dataset(image_count, val_split):
    
    val_size = int(image_count * val_split)
    photo_ds = tf.data.Dataset.list_files(
        str(DATA_DIR / 'エラティカ ニ/*jpg'), shuffle=False
        )#.take(image_count // 2)
    illus_ds = tf.data.Dataset.list_files(
        str(DATA_DIR / 'エラティカ 三/*jpg'), shuffle=False
        )#.take(image_count // 2)
    
    list_ds = photo_ds.concatenate(illus_ds).shuffle(image_count)
    list_ds = list_ds.map(process_path, num_parallel_calls=AUTOTUNE)
    print(tf.data.experimental.cardinality(list_ds).numpy())
    
    return list_ds.skip(val_size), list_ds.take(val_size)

def process_path(file_path):
    
    label = tf.strings.split(file_path, os.sep)[-2]
    image = tf.image.decode_jpeg(tf.io.read_file(file_path), channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, [IMG_HEIGHT, IMG_WIDTH])

    return image, label

cp_callback = keras.callbacks.ModelCheckpoint(
    filepath=CHECKPOINT, 
    save_weights_only=True,
    save_freq=2
    )
train_ds, valid_ds = get_dataset(IMG_COUNT, 0.2)
train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
valid_ds = valid_ds.cache().prefetch(buffer_size=AUTOTUNE)

print(
    f'Found {IMG_COUNT} files belonging to 2 classes\nUsing', tf.data.experimental.cardinality(valid_ds).numpy(), f'files for validation.'
    )

print(train_ds)
print(train_ds.take(1))
raise ValueError
model = tf.keras.Sequential([
    keras.layers.experimental.preprocessing.Rescaling(1./255),
    keras.layers.Conv2D(32, 3, activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Conv2D(32, 3, activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Conv2D(32, 3, activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Conv2D(32, 3, activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Flatten(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(2)
    ])
model.compile(
    optimizer='adam',
    loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
    )
model.fit(
    train_ds,
    validation_data=valid_ds,
    epochs=EPOCHS,
    callbacks=[cp_callback]
    )
# model.save(rf'Machine Learning\{MODEL_NAME}', save_format='tf')