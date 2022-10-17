from PyQt5.QtWidgets import QApplication

from GUI.machinelearning.DesignView import Design

Qapp = QApplication([])

app = Design()
app.showMaximized()

Qapp.exec_()
