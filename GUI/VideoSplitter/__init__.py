'''
Experimental. App for splitting video into clips using the scenedetect module.
'''

from dotenv import load_dotenv
from scenedetect.detectors import ContentDetector
from scenedetect import VideoManager, SceneManager, FrameTimecode

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar, QProgressDialog
from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal, pyqtSlot

from GUI import Worker
from GUI.videosplitter.fileView import FileExplorer
from GUI.videosplitter.videoView import Video
from GUI.videosplitter.clipsView import Clips
from GUI.videosplitter.filmstripView import Filmstrip
    
THRESHOLD = 50
MINIMUM = 15
DOWNSCALE = 50

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
        
        self.scene_manager = SceneManager()
        self.scene_manager.add_detector(ContentDetector(THRESHOLD, MINIMUM))
        
        self.threadpool = QThreadPool(self)
        self.files = FileExplorer(self)
        self.video = Video(self)
        self.clips = Clips(self)
        self.filmstrip = Filmstrip(self)

        self.hlayout.addWidget(self.files, 1)
        self.hlayout.addWidget(self.video, 2)
        self.hlayout.addWidget(self.clips, 1)
        self.vlayout.addWidget(self.timeline, 1)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)
        
        self.files.selection.connect(self.file_selected)

    def create_menu(self):
        
        self.menubar = self.menuBar()

        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction('Exit')
        
        # Tools
        tools = self.menubar.addMenu('Tools')
        tools.addAction('Detect scenes')
        
        # View
        view = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')

    def file_selected(self, select, deselect):
        
        try: index = select.indexes()[0]
        except IndexError: return
        file = index.data(Qt.UserRole + 1)
        
        self.filmstrip.set_filmstrip(file)
        self.video.update(file)
    
    def detect_scenes(self, filepath):
        
        self.progress = QProgressDialog(
            'Processing file...', 'Cancel', 0, 1, self,
            )
        video_manager = VideoManager([str(filepath)])
        video_manager.set_downscale_factor(DOWNSCALE)
        video_manager.start()
        self.frame_num = video_manager.get_duration()[0].get_frames()
        
        worker = Worker(self.scene_manager.detect_scenes, 
            frame_source=video_manager, show_progress=False,             callback=self.updateProgressBar,
            )
        worker.signals.progress.connect(self.updateProgressBar)
        # worker.signals.result.connect(self.get_scene_list)
        worker.signals.finished.connect(self.get_scene_list)
        self.threadpool.start(worker)
    
    def get_scene_list(self):
        
        self.scene_manager.get_cut_list()
    
    def updateProgressBar(self, *value):
        
        print(value[1])
        self.progress.setValue((value[1] * 100) // self.frame_num)
        
    def menuPressEvent(self, event=None):

        action = event.text()
        
        # File
        if action == 'Exit': self.close()
        
        # Tools
        if action == 'Detect scenes':
            
            current = self.files.currentIndex()
            filepath = current.data(Qt.ItemDataRole.UserRole + 1)
            self.detect_scenes(filepath)

    def keyPressEvent(self, event):

        match event.key():

            case Qt.Key.Key_Escape: self.close()
        
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