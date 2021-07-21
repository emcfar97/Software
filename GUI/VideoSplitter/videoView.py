from PyQt5.QtWidgets import QWidget, QLabel

class Video(QLabel):
     
    def __init__(self, parent):
         
        super(Video, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.setStyleSheet('background: green')
        self.setText('video')

    def create_widgets(self):
        
        pass
