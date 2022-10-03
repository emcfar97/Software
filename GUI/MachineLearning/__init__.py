from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QStatusBar, QAction
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from GUI.machinelearning.DesignView import Design
from GUI.machinelearning.DatasetView import Dataset
from GUI.machinelearning.TrainView import Train

class MachineLearning(QMainWindow):

    populateGallery = pyqtSignal()
    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        
        super(MachineLearning, self).__init__()
        self.setWindowTitle('Machine Learning')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)  
        self.stack.setContentsMargins(0, 0, 5, 0)

    def create_widgets(self):
        
        self.design = Design(self)
        self.dataset = Dataset(self)
        self.train = Train(self)
        
        self.stack.addWidget(self.design)
        self.stack.addWidget(self.dataset)
        self.stack.addWidget(self.train)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

    def create_menu(self):
        
        self.menubar = self.menuBar()
        self.tooblar = self.addToolBar('')

        # File
        file = self.menubar.addMenu('File')
        self.create_action(
            file, ['New...', 'Create new project'], self.menuPressEvent, 'Ctrl+N'
            )
        self.create_action(
            file, ['Open...', 'Load project from file'], self.menuPressEvent, 'Ctrl+O'
            )
        file.addMenu('Open recent')
        file.addSeparator()
        self.create_action(
            file, ['Save', 'Save project to file'], self.menuPressEvent, 'Ctrl+S'
            )
        file.addAction('Save As...', self.menuPressEvent, shortcut='Ctrl+Shift+S')
        file.addAction('Save a Copy...', self.menuPressEvent)
        file.addAction('Save Selection...', self.menuPressEvent)
        file.addAction('Export...', self.menuPressEvent)
        file.addSeparator()
        file.addAction('Close', self.menuPressEvent, shortcut='Ctrl+F4')
        file.addSeparator()
        file.addAction('Properties', self.menuPressEvent)
        file.addSeparator()
        file.addAction('Quit', self.menuPressEvent, shortcut='Ctrl+Q')

        # Edit
        edit = self.menubar.addMenu('Edit')
        edit.addAction('Undo', self.menuPressEvent, shortcut='Ctrl+Z')
        edit.addAction('Redo', self.menuPressEvent, shortcut='Ctrl+Y')
        edit.addSeparator()
        edit.addAction('Cut', self.menuPressEvent, shortcut='Ctrl+X')
        edit.addAction('Copy', self.menuPressEvent, shortcut='Ctrl+C')
        edit.addAction('Paste', self.menuPressEvent, shortcut='Ctrl+V')
        edit.addAction('Delete', self.menuPressEvent, shortcut='Del')
        edit.addSeparator()
        edit.addAction('Select All', self.menuPressEvent, shortcut='Ctrl+A')
        edit.addAction('Find', self.menuPressEvent, shortcut='Ctrl+F')
        edit.addSeparator()
        edit.addAction('Preferences', self.menuPressEvent)

        # View
        view = self.menubar.addMenu('View')
        view.addAction('Palettes', self.menuPressEvent, shortcut='F9')
        view.addAction('Inspector', self.menuPressEvent, shortcut='F8')
        view.addSeparator()
        view.addAction('Zoom in', self.menuPressEvent, shortcut='Ctrl++')
        view.addAction('Zoom out', self.menuPressEvent, shortcut='Ctrl+-')
        view.addSeparator()
        view.addAction('Fulscreen', self.menuPressEvent, shortcut='F11')

        # Layer
        layer = self.menubar.addMenu('Layer')

        # Tools
        tools = self.menubar.addMenu('Tools')

        # Help
        help = self.menubar.addMenu('Help')

    def create_action(self, menu, text, slot, shortcut):
        
        if isinstance(text, list): 
            menu.addAction(text[0], self.menuPressEvent, shortcut=shortcut)
            self.tooblar.addAction(
                QAction(QIcon.fromTheme('new.bmp'), f'{text[1]} ({shortcut})', self)
                )
        else:
            menu.addAction(text, self.menuPressEvent, shortcut=shortcut)

    def menuPressEvent(self, event=None):
        
        action = event.text()
        print(action)

    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key_Escape: self.close()
        
        else: self.key_pressed.emit(event)
            
    def closeEvent(self, event):
        
        self.closedWindow.emit(self)