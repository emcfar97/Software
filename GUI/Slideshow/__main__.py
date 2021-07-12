from PyQt5.QtWidgets import QApplication

from GUI.Slideshow import Slideshow

Qapp = QApplication([])

app = Slideshow()

Qapp.exec_()
