from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,  QStackedWidget, QMessageBox, QStatusBar, QGroupBox, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt

from GUI.managedata import ManageData
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview, Timer
from GUI.machinelearning import MachineLearning
from GUI.videosplitter import VideoSplitter

class App(QMainWindow):
    
    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.show()
        
    def configure_gui(self):
        
        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()

        self.setGeometry(
            int(width * .34), int(height * .29),
            int(width * .35), int(height * .48)
            )
        self.frame = QGroupBox()
        self.layout = QVBoxLayout()
        self.frame.setLayout(self.layout) 

        self.layout.setAlignment(Qt.AlignHCenter)
        self.setContentsMargins(10, 10, 10, 15)
        self.frame.setFixedHeight(height // 3)
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
    
    def select(self, title, app):
        
        app = app(self)
        app.window_closed.connect(self.closed_window)
        self.windows[title] = self.windows.get(title, []) + [app]
        self.hide()
        
    def closed_window(self, event):
        
        widget = event
        self.windows[widget.windowTitle()].remove(widget)
        if any(self.windows.values()): self.show()

    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        ctrl = modifiers == Qt.ControlModifier

        if ctrl:

            if key_press == Qt.Key_1: self.select('Manage Data', ManageData)

            elif key_press == Qt.Key_2: self.select('Gesture Draw', GestureDraw)

            elif key_press == Qt.Key_3: self.select('Machine Learning', MachineLearning)

        elif key_press in (Qt.Key_Return, Qt.Key_Enter): 
            
            if not self.isHidden(): self.focusWidget().click()

        elif key_press == Qt.Key_Escape: self.close()

    def closeEvent(self, event):
        
        Qapp.quit()

class GestureDraw(QMainWindow):
    
    def __init__(self, parent):
        
        super(GestureDraw, self).__init__()
        self.setWindowTitle('Gesture Draw')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.show()
        self.gallery.populate()

    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)  

        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width // 2, height)

    def create_widgets(self):
        
        self.gallery = Gallery(self, (5, 0, 5, 0))
        self.preview = Preview(self, 'black')
        self.timer = Timer(self.preview)

        self.gallery.ribbon.multi.setChecked(True)
        self.gallery.ribbon.changeSelectionMode(True)
        self.stack.addWidget(self.gallery)
        self.stack.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)
        
    def start_session(self):
        
        gallery = iter(
            self.gallery.images.selectedIndexes()
            )
        time = self.gallery.ribbon.time.text()
        
        if gallery and time:

            self.statusbar.hide()

            if ':' in time:
                min, sec = time.split(':')
                time = (int(min) * 60) + int(sec)
            else: time = int(time)
            
            self.stack.setCurrentIndex(1)
            self.timer.start(gallery, time)
        
        else:
            QMessageBox.information(
                self, '', 
                'You are either missing images or a time',
                QMessageBox.Ok
                )

    def keyPressEvent(self, event):
        
        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter): self.start_session()

        elif key_press == Qt.Key_Space: self.timer.pause()

        elif key_press == Qt.Key_Escape:

            if self.stack.currentIndex():
                
                self.timer.pause()
                self.statusbar.show()
                self.statusbar.showMessage('')
                self.stack.setCurrentIndex(0)
                self.gallery.populate()
                            
            else: self.close()
        
        else: self.parent.keyPressEvent(event)

    def closeEvent(self, event):
    
        if self.stack.currentIndex():
            
            self.timer.pause()
            self.statusbar.show()
            self.statusbar.showMessage('')
            self.stack.setCurrentIndex(0)
            self.gallery.populate()

        else:
            self.parent.windows[self.windowTitle()].remove(self)
            if not self.parent.is_empty(): self.parent.show()

Qapp = QApplication([])

app = App()
Qapp.setQuitOnLastWindowClosed(False)

Qapp.exec_()