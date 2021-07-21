from PyQt5.QtWidgets import QApplication

from GUI.managedata import ManageData

Qapp = QApplication([])

app = ManageData()

Qapp.exec_()
