'''
Consists of a lefthand gallery of images and a righthand display for selected image. Allows deletion and updating of records, as well as a slideshow function that can display images and videos in fullscreen.
'''
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal

from GUInew.utils import Authenticate
from GUInew.managedata.galleryView import Gallery
from GUInew.managedata.previewView import Preview
from GUInew.managedata.ribbonView import Ribbon

class ManageData(QMainWindow):

    populateGallery = pyqtSignal()
    closedWindow = pyqtSignal(object)
    
    def __init__(self):

        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.showMaximized()
        self.mysql = Authenticate()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.setSpacing(0)

    def create_widgets(self):

        self.windows = set()

        self.gallery = Gallery(self)
        self.preview = Preview(self, 'white')
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

    def create_menu(self): pass

    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        alt = modifiers == Qt.Modifier.ALT

        if alt:
            
            if key_press == Qt.Key_Left: self.ribbon.go_back()
                
            elif key_press == Qt.Key_Right: self.ribbon.go_forward()
            
        if key_press == Qt.Key.Key_F4: self.ribbon.tags.setFocus()
        
        elif key_press == Qt.Key.Key_F5: self.select_records()

        elif key_press == Qt.Key.Key_Delete:
            
            self.delete_records(self.gallery.selectedIndexes())
                        
        elif key_press == Qt.Key.Key_Escape: self.close()
    
    def closeEvent(self, event):
        
        self.mysql.close()
        for window in self.windows: window.close()
        self.closedWindow.emit(self)