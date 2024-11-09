from PyQt6.QtWidgets import QApplication

from GUI.deeplearning import DeepLearning

Qapp = QApplication([])

app = DeepLearning()
Qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

Qapp.exec()