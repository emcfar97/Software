from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PyQt5.QtCore import Qt

from GUI.videosplitter.fileView import FileExplorer
from GUI.videosplitter.videoView import Video
from GUI.videosplitter.clipsView import Clips
from GUI.videosplitter.timelineView import Timeline

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
        self.vlayout = QVBoxLayout() 
        self.hlayout = QHBoxLayout()

        self.center.setLayout(self.vlayout)
        self.setCentralWidget(self.center)
        self.vlayout.setContentsMargins(9, 9, 9, 0)
        self.vlayout.addLayout(self.hlayout, 3)

    def create_widgets(self):
        
        self.files = FileExplorer(self)
        self.video = Video(self)
        self.clips = Clips(self)
        self.timeline = Timeline(self)

        self.hlayout.addWidget(self.files, 1)
        self.hlayout.addWidget(self.video, 2)
        self.hlayout.addWidget(self.clips, 1)
        self.vlayout.addWidget(self.timeline, 1)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

    def create_menu(self):
        
        self.menubar = self.menuBar()

        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        
        # View
        help = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')

    def menuPressEvent(self, event=None):

        action = event.text()

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