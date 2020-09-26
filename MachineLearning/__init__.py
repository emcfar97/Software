from PIL import Image
from pathlib import Path
from numpy import resize, array, loadtxt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

HOME = Path(__file__).parent
MODELS = HOME / 'Models'
CHCKPNT = HOME / 'Checkpoints'
LOGS = HOME / 'Logs'

class Model():

    def __init__(self, path):
        
        self.path = MODELS / path
        self.model = keras.models.load_model(self.path, compile=False)
        self.labels = loadtxt(
            self.path.with_name(f'{self.path.stem.split("-")[0]}.txt'), 
            dtype='<U44'
            )
        self.shape = self.model.input_shape
    
    def build(self): pass

    def train(self): pass

    def predict(self, image, threshold=0.1):

        image = resize(array(Image.open(image)), (1, *self.shape[1:]))
        scores = self.model.predict(image).reshape(*self.labels.shape)
        
        if self.labels.size == 2: return self.labels[scores.argmax()]
        return [
            self.labels[score] for score in 
            range(*self.labels.shape)
            if scores[score] > threshold
            ]

    def summary(self): return self.model.summary()

    def save(self, name):

        self.model.save(MODELS / name.with_suffix('hdf5'), save_format='h5')