import tensorflow as tf
import keras

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import Qt, pyqtSignal

class Train(QWidget):

    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent=None, model=None):
        
        super(Train, self).__init__(parent)
        if model: self.model = model
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
    
        self.layout = QHBoxLayout(self)
        
    def create_widgets(self):
    
        self.start = QPushButton('Start', self)
        self.layout.addWidget(self.start)

    def train(self):
                
        mnist = tf.keras.datasets.mnist

        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        predictions = self.model(x_train[:1]).numpy()

        loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        loss_fn(y_train[:1], predictions).numpy()

        tracking = keras.callbacks.LambdaCallback(
            on_epoch_end=self.log, 
            on_train_begin=self.log, 
            on_train_end=self.log
            )
        # keras.callbacks.LearningRateScheduler(schedule, verbose=0)
        
        self.model.compile(
            optimizer='adam',
            loss=loss_fn,
            metrics=['accuracy'],
            callbacks=[tracking], 
            )

        self.model.fit(x_train, y_train, epochs=5)
    
    def log(self, *logs):
        
        if len(logs) == 2: 
            
            epoch, logs = logs
        
        else: pass
        
    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key_Escape: self.close()
        
        else: self.key_pressed.emit(event)
        
