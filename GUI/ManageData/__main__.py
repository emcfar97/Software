from PyQt6.QtWidgets import QApplication

from GUI.managedata import ManageData

Qapp = QApplication([])

app = ManageData()
Qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

Qapp.exec()