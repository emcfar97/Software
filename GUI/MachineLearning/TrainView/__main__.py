from PyQt5.QtWidgets import QApplication

from GUI.machinelearning.TrainView import Train

Qapp = QApplication([])

app = Train()

Qapp.exec_()
