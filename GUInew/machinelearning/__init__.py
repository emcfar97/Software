'''
Experimental. App for GUI-ifying the machine learning process, a la PerceptiLabs.
'''

from dotenv import load_dotenv
from PyQt6.QtWidgets import QMainWindow

class MachineLearning(QMainWindow):

    def __init__(self):

        super(MachineLearning, self).__init__()
        self.setWindowTitle('')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self): pass

    def create_widgets(self): pass

    def create_menu(self): pass