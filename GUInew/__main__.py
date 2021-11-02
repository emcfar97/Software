from PyQt6.QtWidgets import QApplication
from . import App

Qapp = QApplication([])

app = App()
Qapp.setQuitOnLastWindowClosed(False)

Qapp.exec()