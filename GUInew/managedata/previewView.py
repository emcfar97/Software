from PyQt6.QtWidgets import QScrollArea

class Preview(QScrollArea):
    
    def __init__(self, parent, color):
        
        super(Preview, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
    
    def configure_gui(self):

        self.setStyleSheet('color: red')

    def create_widgets(self): pass

    def create_menu(self): pass
    