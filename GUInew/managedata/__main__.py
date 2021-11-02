from PyQt6.QtWidgets import QApplication

from GUInew.managedata import ManageData

Qapp = QApplication([])

app = ManageData()

Qapp.exec()