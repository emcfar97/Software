from PyQt5.QtWidgets import QMainWindow, QVBoxLayout,  QStackedWidget, QMessageBox, QStatusBar, QGroupBox, QPushButton, QSizePolicy, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class MachineLearning(QMainWindow):
    
    def __init__(self, parent=None):
        
        super(MachineLearning, self).__init__(parent)
        self.setWindowTitle('Machine Learning')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)  
        # self.stack.setContentsMargins(0, 0, 5, 0)

    def create_menu(self):
        
        self.menubar = self.menuBar()
        self.tooblar = self.addToolBar('')

        # File
        file = self.menubar.addMenu('File')
        self.create_action(
            file, ['New...', 'Create new project'], self.menuAction, 'Ctrl+N'
            )
        self.create_action(
            file, ['Open...', 'Load project from file'], self.menuAction, 'Ctrl+O'
            )
        file.addMenu('Open recent')
        file.addSeparator()
        self.create_action(
            file, ['Save', 'Save project to file'], self.menuAction, 'Ctrl+S'
            )
        file.addAction('Save As...', self.menuAction, shortcut='Ctrl+Shift+S')
        file.addAction('Save a Copy...', self.menuAction)
        file.addAction('Save Selection...', self.menuAction)
        file.addAction('Export...', self.menuAction)
        file.addSeparator()
        file.addAction('Close', self.menuAction, shortcut='Ctrl+F4')
        file.addSeparator()
        file.addAction('Properties', self.menuAction)
        file.addSeparator()
        file.addAction('Quit', self.menuAction, shortcut='Ctrl+Q')

        # Edit
        edit = self.menubar.addMenu('Edit')
        edit.addAction('Undo', self.menuAction, shortcut='Ctrl+Z')
        edit.addAction('Redo', self.menuAction, shortcut='Ctrl+Y')
        edit.addSeparator()
        edit.addAction('Cut', self.menuAction, shortcut='Ctrl+X')
        edit.addAction('Copy', self.menuAction, shortcut='Ctrl+C')
        edit.addAction('Paste', self.menuAction, shortcut='Ctrl+V')
        edit.addAction('Delete', self.menuAction, shortcut='Del')
        edit.addSeparator()
        edit.addAction('Select All', self.menuAction, shortcut='Ctrl+A')
        edit.addAction('Find', self.menuAction, shortcut='Ctrl+F')
        edit.addSeparator()
        edit.addAction('Preferences', self.menuAction)

        # View
        view = self.menubar.addMenu('View')
        view.addAction('Palettes', self.menuAction, shortcut='F9')
        view.addAction('Inspector', self.menuAction, shortcut='F8')
        view.addSeparator()
        view.addAction('Zoom in', self.menuAction, shortcut='Ctrl++')
        view.addAction('Zoom out', self.menuAction, shortcut='Ctrl+-')
        view.addSeparator()
        view.addAction('Fulscreen', self.menuAction, shortcut='F11')

        # Layer
        layer = self.menubar.addMenu('Layer')

        # Tools
        tools = self.menubar.addMenu('Tools')

        # Help
        help = self.menubar.addMenu('Help')

    def create_action(self, menu, text, slot, shortcut):
        
        if isinstance(text, list): 
            menu.addAction(text[0], self.menuAction, shortcut=shortcut)
            self.tooblar.addAction(
                QAction(QIcon('new.bmp'), f'{text[1]} ({shortcut})', self)
                )
        else:
            menu.addAction(text, self.menuAction, shortcut=shortcut)

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

    def menuPressEvent(self, action=None):

        print(action)

    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key_Escape: self.close()

    def closeEvent(self, event):
        
        self.parent.windows[self.windowTitle()].remove(self)
        if not self.parent.is_empty(): self.parent.show()