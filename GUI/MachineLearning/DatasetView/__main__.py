from PyQt5.QtWidgets import QApplication

from GUI.machinelearning.DatasetView import Dataset

Qapp = QApplication([])

app = Dataset()

Qapp.exec_()
