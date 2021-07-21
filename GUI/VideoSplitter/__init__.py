from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PyQt5.QtCore import Qt

from GUI.videosplitter.videoView import Video
from GUI.videosplitter.fileView import FileExplorer
from GUI.videosplitter.timelineView import Timeline
from GUI.videosplitter.clipsView import Clips

class VideoSplitter(QMainWindow):

    def __init__(self, parent=None):
    
        super(VideoSplitter, self).__init__()
        self.setWindowTitle('Video Splitter')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.showMaximized()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout() 

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def create_widgets(self):
        
        self.video = Video(self)
        self.files = FileExplorer(self)
        self.timeline = Timeline(self)
        self.clips = Clips(self)

        self.layout.addWidget(self.video)
        self.layout.addWidget(self.files)
        self.layout.addWidget(self.timeline)
        self.layout.addWidget(self.clips)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

    def create_menu(self): pass

    def keyPressEvent(self, event):

        key_press = event.key()

        if key_press == Qt.Key_Escape: self.close()
    
        elif self.parent is not None:
            
            self.parent.keyPressEvent(event)

class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass