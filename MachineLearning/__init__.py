from pathlib import Path
import numpy as np

HOME = Path(__file__).parent
DATA = HOME / 'Datasets'
BATCH = 64
HEIGHT = 256
WIDTH = 256
EPOCH = 10

# class Model():

    # def __init__(self, path):
        
    #     self.path = MODELS / path
    #     self.model = keras.models.load_model(self.path, compile=False)
    #     self.labels = loadtxt(
    #         self.path.with_name(
    #             self.path.name.split('-')[0]
    #             ).with_suffix('.txt'), 
    #         dtype='<U44'
    #         )
    #     self.type = self.labels[0]
    #     self.labels = self.labels[1:]
    #     self.shape = self.model.input_shape
    
    # def build(self): pass

    # def train(self): pass

    # def predict(self, image, threshold=0.3):

    #     image = resize(array(Image.open(image)), (1, *self.shape[1:]))
    #     scores = self.model.predict(image)

    #     if scores.size == 1: return self.labels[int(scores < threshold)]

    #     elif self.type == '__single__': return self.labels[scores.argmax()]
        
    #     return [self.labels[j] for i, j in argwhere(scores > threshold)]

    # def summary(self): return self.model.summary()

    # def save(self, name=None):

    #     if name: name = MODELS / name.with_suffix('hdf5')
    #     else: name = self.path
        
    #     self.model.save(name, save_format='h5')