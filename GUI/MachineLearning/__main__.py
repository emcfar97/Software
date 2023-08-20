from PyQt6.QtWidgets import QApplication
from GUI.machinelearning import MachineLearning

Qapp = QApplication([])

app = MachineLearning()
Qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

Qapp.exec()