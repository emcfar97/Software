from PyQt5.QtWidgets import QApplication

from GUI.machinelearning.DatasetView import Dataset

Qapp = QApplication([])

app.showMaximized()
app = Dataset()

Qapp.exec_()
