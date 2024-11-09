from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

class Dataset(QMainWindow):

    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        
        super(Dataset, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        
        self.label = QLabel(self)
        self.label.setStyleSheet('background: blue')
        self.setCentralWidget(self.label) 
        # self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return
    
        self.layout = QHBoxLayout(self)
    
    def create_widgets(self): pass

    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key.Key_Escape: self.close()
        
        else: self.key_pressed.emit(event)