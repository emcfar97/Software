'''
Experimental. App for splitting video into clips using the scenedetect module.
'''

from dotenv import load_dotenv
from scenedetect.detectors import ContentDetector
from scenedetect import VideoManager, SceneManager, FrameTimecode

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from GUI.videosplitter.fileView import FileExplorer
from GUI.videosplitter.videoView import Video
from GUI.videosplitter.clipsView import Clips
from GUI.videosplitter.timelineView import Timeline

class VideoSplitter(QMainWindow):

    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)
    
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
        file.addAction('Exit')
        
        # View
        view = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')

    def menuPressEvent(self, event=None):
        
        match event.text():
        
            # File
            case 'Exit': self.close()

    def keyPressEvent(self, event):

        match event.key():

            case Qt.Key_Escape: self.close()
        
            case _: self.key_pressed.emit(event)

    def closeEvent(self, event):
        
        self.closedWindow.emit(self)
        
class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass