'''File for dataset logic'''

import os
from .. import DATA, BATCH, HEIGHT, WIDTH, np
from . import *

class Custom_Dataset(object):

    def __init__(self, main_dir):

        self.main_dir = DATA / main_dir
        self.data = tf.data.Dataset.list_files(
            str(self.main_dir / '*/*'), shuffle=False
            )
        self.class_names = np.array([
            item.name for item in self.main_dir.glob('*') if item.is_dir()
            ])

    def __len__(self): return self.data.cardinality().numpy()
    
    def load_data(self, split=.2):

        val_size = int(len(self) * split)

        train_ds = self.data.skip(val_size)
        val_ds = self.data.take(val_size)

        train_ds = train_ds.map(
            self.process_path, num_parallel_calls=tf.data.AUTOTUNE
            )
        val_ds = val_ds.map(
            self.process_path, num_parallel_calls=tf.data.AUTOTUNE
            )
        
        train_ds = self.configure_for_performance(train_ds)
        val_ds = self.configure_for_performance(val_ds)

        return train_ds, val_ds
    
    def configure_for_performance(self, ds):
  
        ds = ds.cache()
        ds = ds.shuffle(buffer_size=1000)
        ds = ds.batch(BATCH)
        ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)
  
        return ds
    
    def get_label(self, file_path):

        # convert the path to a list of path components
        parts = tf.strings.split(file_path, os.path.sep)
        # The second to last is the class-directory
        one_hot = parts[-2] == self.class_names
        # Integer encode the label
        return tf.argmax(one_hot)

    def decode_img(self, img):

        # convert the compressed string to a 3D uint8 tensor
        img = tf.image.decode_jpeg(img, channels=3)
        # resize the image to the desired size
        return tf.image.resize(img, [HEIGHT, WIDTH])

    def process_path(self, file_path):

        label = self.get_label(file_path)
        # load the raw data from the file as a string
        img = tf.io.read_file(file_path)
        img = self.decode_img(img)

        return img, label