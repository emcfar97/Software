from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal

class Dataset(QWidget):

    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        
        super(Dataset, self).__init__(parent)
        # self.layout = QHBoxLayout(self)
        self.create_widgets()

    def configure_gui(self): pass
    
    def create_widgets(self): pass

    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key_Escape: self.close()
        
        else: self.key_pressed.emit(event)