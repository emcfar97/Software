from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QWidget

ENUM = {
    'All': '',
    'Photo': "type='photograph'",
    'Illus': "type='illustration'",
    'Comic': "type='comic'",
    'Explicit': '',
    'Questionable': 'rating<3',
    'Safe': 'rating=1',
    }

class Ribbon(QWidget):
     
    selection_mode = pyqtSignal(bool)

    def __init__(self, parent):
         
        super(Ribbon, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.undo = ['']
        self.redo = []
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 5, 0)

    def create_widgets(self): pass    