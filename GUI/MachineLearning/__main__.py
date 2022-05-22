from PyQt5.QtWidgets import QApplication

from GUI.machinelearning import MachineLearning

Qapp = QApplication([])

app = MachineLearning()

Qapp.exec_()
