from PyQt6.QtWidgets import QTableView
from PyQt6.QtCore import pyqtSignal, QModelIndex, QItemSelection

COLUMNS = 5.18

class Gallery(QTableView):
    
    selection = pyqtSignal(QItemSelection, QItemSelection)
    find_artist = pyqtSignal(QModelIndex)
    delete = pyqtSignal(list)
    load_comic = pyqtSignal(object)

    def __init__(self, parent): 

        super(Gallery, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        
    
    def configure_gui(self):

        self.setStyleSheet('color: red')

    def create_widgets(self): pass

    def create_menu(self): pass