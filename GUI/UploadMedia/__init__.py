from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QTableView, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QRadioButton, QComboBox, QDialog, QScrollArea
from PyQt5.QtCore import Qt

SITES = {
    'deviantart': [],
    'foundry': [],
    'instagram': [],
    'pixiv': [],
    'twitter': [],
    }

class UploadMedia(QMainWindow):
     
    def __init__(self, parent):
         
        super(UploadMedia).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.layout = QHBoxLayout()
        pass
    
    def create_widgets(self):
        
        pass
    