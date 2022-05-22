from PyQt5.QtWidgets import QWidget, QLabel
    
class FileExplorer(QLabel):
     
    def __init__(self, parent):
         
        super(FileExplorer, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.setStyleSheet('background: red')
        self.setText('files')

    def create_widgets(self):
        
        pass