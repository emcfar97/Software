from PyQt5.QtWidgets import QWidget

class Dataset(QWidget):

    def __init__(self, parent):
        
        super(Dataset, self).__init__(parent)
        # self.layout = QHBoxLayout(self)
        self.create_widgets()

    def configure_gui(self): pass
    
    def create_widgets(self): pass
