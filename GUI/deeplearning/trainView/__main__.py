import keras
from PyQt.QtWidgets import QApplication

from GUI.deeplearning.trainView import Train

Qapp = QApplication([])

model = keras.models.load_model(r'GUI\machinelearning\TrainView\test.hdf5')
        
app = Train(model=model)
app.showMaximized()

Qapp.exec()