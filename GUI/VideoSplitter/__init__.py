from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QTableView, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QRadioButton, QComboBox, QDialog, QScrollArea
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QAbstractTableModel

class VideoSplitter(QMainWindow):

    def __init__(self, parent):
        
        super(VideoSplitter, self).__init__(parent)
        self.setWindowTitle('Video Splitter')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.layout = QStackedWidget(self)
        self.setCentralWidget(self.layout)  

    def create_widgets(self):
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

class Ribbon():
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass
    
class Canvas():
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass
    
class FileExplorer():
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass

class Timeline():
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass

class VideoClips():
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        pass
    
    def create_widgets(self):
        
        pass