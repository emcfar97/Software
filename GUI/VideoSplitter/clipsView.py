from PyQt5.QtWidgets import QWidget, QLabel

class Clips(QLabel):
     
    def __init__(self, parent):
         
        super(Clips, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.setStyleSheet('background: blue')
        self.setText('clips')

    def create_widgets(self):
        
        pass
