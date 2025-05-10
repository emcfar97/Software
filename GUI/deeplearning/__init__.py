from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QAction

from GUI.deeplearning.designView import Design
from GUI.deeplearning.datasetView import Dataset
from GUI.deeplearning.trainView import Train

class DeepLearning(QMainWindow):

    populateGallery = pyqtSignal()
    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        
        super(DeepLearning, self).__init__()
        self.setWindowTitle('Deep Learning')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setStyleSheet('''
            QTabWidget::tab-bar {alignment: center;}
            ''')
        self.tab_widget.setContentsMargins(0, 0, 5, 0)
        self.setCentralWidget(self.tab_widget)

    def create_widgets(self):
        
        self.design = Design(self)
        self.dataset = Dataset(self)
        self.train = Train(self)
        
        self.tab_widget.addTab(self.design, 'Design')
        self.tab_widget.addTab(self.dataset, 'Dataset')
        self.tab_widget.addTab(self.train, 'Train')

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
        file.addAction('Save As...', 'Ctrl+Shift+S', self.menuPressEvent)
        file.addAction('Save a Copy...', self.menuPressEvent)
        file.addAction('Save Selection...', self.menuPressEvent)
        file.addAction('Export...', self.menuPressEvent)
        file.addSeparator()
        file.addAction('Close', 'Ctrl+F4', self.menuPressEvent)
        file.addSeparator()
        file.addAction('Properties', self.menuPressEvent)
        file.addSeparator()
        file.addAction('Quit', 'Ctrl+Q', self.menuPressEvent)

        # Edit
        edit = self.menubar.addMenu('Edit')
        edit.addAction('Undo', 'Ctrl+Z', self.menuPressEvent)
        edit.addAction('Redo', 'Ctrl+Y', self.menuPressEvent)
        edit.addSeparator()
        edit.addAction('Cut', 'Ctrl+X', self.menuPressEvent)
        edit.addAction('Copy', 'Ctrl+C', self.menuPressEvent)
        edit.addAction('Paste', 'Ctrl+V', self.menuPressEvent)
        edit.addAction('Delete', 'Del', self.menuPressEvent)
        edit.addSeparator()
        edit.addAction('Select All', 'Ctrl+A', self.menuPressEvent)
        edit.addAction('Find', 'Ctrl+F', self.menuPressEvent)
        edit.addSeparator()
        edit.addAction('Preferences', self.menuPressEvent)

        # View
        view = self.menubar.addMenu('View')
        view.addAction('Palettes', 'F9', self.menuPressEvent)
        view.addAction('Inspector', 'F8', self.menuPressEvent)
        view.addSeparator()
        view.addAction('Zoom in', 'Ctrl++', self.menuPressEvent)
        view.addAction('Zoom out', 'Ctrl+-', self.menuPressEvent)
        view.addSeparator()
        view.addAction('Fulscreen', 'F11', self.menuPressEvent)

        # Tools
        tools = self.menubar.addMenu('Tools')

        # Help
        help = self.menubar.addMenu('Help')

    def create_action(self, menu, text, slot, shortcut):
        
        if isinstance(text, list): 
            
            menu.addAction(text[0], shortcut, self.menuPressEvent)
            self.tooblar.addAction(
                QAction(QIcon.fromTheme('new.bmp'), f'{text[1]} ({shortcut})', self)
                )
        else:
            menu.addAction(text, shortcut, self.menuPressEvent)

    def menuPressEvent(self, event=None):
        
        action = event.text()
        print(action)

    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key.Key_Escape: self.close()
        
        else: self.key_pressed.emit(event)
            
    def closeEvent(self, event):
        
        self.closedWindow.emit(self)