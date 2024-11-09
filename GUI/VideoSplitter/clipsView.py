from PyQt6.QtWidgets import QScrollArea, QSizePolicy

class Clips(QScrollArea):
     
    def __init__(self, parent):
         
        super(Clips, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.setStyleSheet('background: yellow')
        self.setText('clips')

    def create_widgets(self):
        
        pass
