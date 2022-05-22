from PyQt5.QtWidgets import QApplication

from GUI.videosplitter import VideoSplitter

Qapp = QApplication([])

app = VideoSplitter()

Qapp.exec_()
