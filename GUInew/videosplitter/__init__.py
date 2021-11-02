'''
Experimental. App for splitting video into clips using the scenedetect module.
'''

from dotenv import load_dotenv
from PyQt6.QtWidgets import QMainWindow
from . import VideoSplitter

class VideoSplitter(QMainWindow):

    def __init__(self):

        super(VideoSplitter, self).__init__()
        self.setWindowTitle('')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self): pass

    def create_widgets(self): pass

    def create_menu(self): pass