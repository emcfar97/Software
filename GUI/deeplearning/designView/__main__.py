from PyQt6.QtWidgets import QApplication

from GUI.deeplearning.designView import Design

Qapp = QApplication([])

app = Design()
app.showMaximized()

Qapp.exec()
