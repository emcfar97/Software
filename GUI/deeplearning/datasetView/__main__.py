from PyQt6.QtWidgets import QApplication

from GUI.deeplearning.datasetView import Dataset

Qapp = QApplication([])

app = Dataset()
app.showMaximized()

Qapp.exec()
