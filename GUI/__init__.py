from dotenv import load_dotenv
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGroupBox, QPushButton, QSizePolicy
from GUIold.__main__ import Qapp

from GUIold.managedata import ManageData
from GUIold.machinelearning import MachineLearning
from GUIold.videosplitter import VideoSplitter

load_dotenv()

class App(QMainWindow):

    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self):
        
        resolution = QScreen.geometry()
        
        self.setBaseSize(
            int(resolution.width() * .35), 
            int(resolution.height() * .48)
            )
        self.frame = QGroupBox()
        self.layout = QVBoxLayout()
        self.frame.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setContentsMargins(10, 10, 10, 15)
        # self.frame.setFixedHeight(height // 3)
        self.setCentralWidget(self.frame)
        
    def create_widgets(self):
        
        self.windows = {}
        options = {
            'Manage Data': ManageData, 
            'Gesture Draw': GestureDraw, 
            'Machine Learning': MachineLearning,
            'Video Splitter': VideoSplitter,
            }
            
        for name, app in options.items():
            
            option = QPushButton(name, self)
            option.setStyleSheet('''
                QPushButton::focus:!hover {background: #b0caef};
                text-align: left;
                padding: 20px;
                font: 12px;
                ''')
            option.clicked.connect(
                lambda checked, x=name, y=app: self.select(x, y)
                )
            option.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
                )
            
            self.layout.addWidget(option)
    
    def create_menu(self): pass

    def select(self, title, app):
        
        app = app(self)
        app.closedWindow.connect(self.closed_window)
        app.key_pressed.connect(self.keyPressEvent)
        self.windows[title] = self.windows.get(title, []) + [app]
        self.hide()

    def closed_window(self, event):

        self.windows[event.windowTitle()].remove(event)
        if not any(self.windows.values()): self.show()

    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        ctrl = modifiers == Qt.KeyboardModifier.ControlModifier

        if ctrl:
            
            match key_press:
                
                case Qt.Key_1: self.select('Manage Data', ManageData)

                case Qt.Key_2: self.select('Gesture Draw', GestureDraw)

                case Qt.Key_3: self.select('Machine Learning', MachineLearning)
                
                case Qt.Key_4: self.select('Video Splitter', VideoSplitter)

        match key_press:
            
            case (Qt.Key_Return, Qt.Key_Enter):
            
                if not self.isHidden(): self.focusWidget().click()

            case Qt.Key_Escape: self.close()

    def closeEvent(self, event): QApplication.quit()

class GestureDraw(QMainWindow):

    populateGallery = pyqtSignal()
    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)

    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self): pass

    def create_widgets(self): pass

    def create_menu(self): pass

    def keyPressEvent(self, event): pass

    def closeEvent(self, event): pass