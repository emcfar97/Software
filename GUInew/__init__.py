from dotenv import load_dotenv
from PyQt6.QtWidgets import QMainWindow

load_dotenv()

class App(QMainWindow):

    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self):
        
        # center widget
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_widgets(self): pass

    def create_menu(self): pass

    def select(self, title, app): pass

    def closed_window(self, event): pass

    def keyPressEvent(self, event): pass

    def closeEvent(self, event): pass

class GestureDraw(QMainWindow):

    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self): pass

    def create_widgets(self): pass

    def create_menu(self): pass

    def keyPressEvent(self, event): pass

    def closeEvent(self, event): pass