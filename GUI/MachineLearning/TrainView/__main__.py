import keras
from PyQt5.QtWidgets import QApplication

from GUI.machinelearning.TrainView import Train

Qapp = QApplication([])

model = keras.models.load_model(r'GUI\machinelearning\TrainView\test.hdf5')
        
app = Train(model)
app.showMaximized()
app.train()

Qapp.exec_()
