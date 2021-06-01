from PyQt5.QtWidgets import QWidget

class Dataset(QWidget):

    def __init__(self, parent):
        
        super(QWidget, self).__init__(parent)
        # self.layout = QHBoxLayout(self)
        self.create_widgets()

    def create_widgets(self): pass
