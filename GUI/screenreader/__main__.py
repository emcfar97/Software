from PyQt6.QtWidgets import QApplication

from GUI.screenreader.__init__ import ScreenReader

Qapp = QApplication([])

app = ScreenReader()
Qapp.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")


Qapp.exec_()
