from PyQt6.QtWidgets import QWidget, QLabel

class Timeline(QLabel):
     
    def __init__(self, parent):
         
        super(Timeline, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.setStyleSheet('background: blue')
        self.setText('timeline')

    def create_widgets(self):
        
        pass
