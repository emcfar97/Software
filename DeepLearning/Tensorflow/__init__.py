'''Tensorflow API'''

import keras
from PIL import Image
import tensorflow as tf
from numpy import resize, array, argwhere, loadtxt
from DeepLearning import HOME

MODELS = HOME / 'Tensorflow' / 'Models'
CHCKPNT = HOME / 'Tensorflow' / 'Checkpoints'
LOGS = HOME / 'Tensorflow' / 'Logs'
AUTOTUNE = tf.data.experimental.AUTOTUNE
BATCH = 32

class Model():
    
    def __init__(self, path=None, text_path=None):
        
        self.path = MODELS / path
        self.model = keras.models.load_model(self.path, compile=False)
        
        if text_path:
            self.labels = loadtxt(
                MODELS / text_path, dtype='<U44'
                )
        else: 
            self.labels = loadtxt(
                self.path.with_name(
                    self.path.name.split('-')[0]
                    ).with_suffix('.txt'), 
                dtype='<U44'
                )
        self.type = self.labels[0]
        self.labels = self.labels[1:]
        self.shape = self.model.input_shape
    
    def build(self): pass

    def data(self):
        
        train_ds = tf.data.Dataset.list_files(
            str(DATA), validation_split=0.2, subset='training', 
            seed=1337, image_size=self.shape, batch_size=BATCH
            )
        val_ds = tf.data.Dataset.list_files(
            str(DATA), validation_split=0.2, subset='validation', 
            seed=1337, image_size=self.shape, batch_size=BATCH
            )
        data_augmentation = keras.Sequential([
            keras.layers.experimental.preprocessing.RandomFlip(),
            keras.layers.experimental.preprocessing.RandomRotation(0.33),
            keras.layers.experimental.preprocessing.RandomZoom(
                height_factor=(-0.3, -0.1),
                width_factor=(-0.3, -0.1)
                ),
            ])
        augmented_train_ds = train_ds.map(
            lambda x, y: (data_augmentation(x, training=True), y)
            )

        train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
        val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)
        
        return train_ds, val_ds
        
    def train(self, epochs, DATA, logging=True): 
                
        train_ds, val_ds = self.data(DATA)
        
        checkpoint = keras.callbacks.ModelCheckpoint(
            CHCKPNT / f'{NAME}_{{epoch:02}}.hdf5'
            )
        if logging: tensorboard = keras.callbacks.TensorBoard(
            log_dir=LOGS / f'{NAME}-{VERSION:02}', histogram_freq=1
            )
        save_callback = keras.callbacks.LambdaCallback(
            on_epoch_end=self.save_model
            )
        
        self.build()
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
            )
        self.model.fit(
            train_ds, validation_data=val_ds, epochs=EPOCHS + INITIAL, 
            callbacks=[checkpoint, tensorboard, save_callback], 
            initial_epoch=INITIAL, verbose=1
            )
        self.model.save(MODELS / f'{NAME}-{VERSION:02}.hdf5', save_format='h5')

    def predict(self, image, threshold=0.3):

        image = resize(array(Image.open(image)), (1, *self.shape[1:]))
        scores = self.model.predict(image)

        if scores.size == 1: return self.labels[int(scores < threshold)]

        elif self.type == '__single__': return self.labels[scores.argmax()]
        
        return [self.labels[j] for i, j in argwhere(scores > threshold)]

    def summary(self): return self.model.summary()

    def save(self, name=None):
        'Save weights of model to hdf5 file'

        if name: name = MODELS / name.with_suffix('hdf5')
        else: name = self.path
        
        self.model.save(name, save_format='h5')
        
    
    def save_model(self, epoch, logs):
        'Callback function which saves model every 2 epochs'

        factors = [i for i in range(2, epoch) if not epoch % i]
        if factors: 
            
            save = factors[len(factors) // 2]
        
            if not epoch % save:
                
                self.save(
                    MODELS / f'{NAME}-{VERSION:02}.hdf5', save_format='h5'
                    )