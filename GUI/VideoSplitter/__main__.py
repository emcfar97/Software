from PyQt5.QtWidgets import QApplication

from GUI.VideoSplitter import VideoSplitter

Qapp = QApplication([])

app = VideoSplitter()

Qapp.exec_()
