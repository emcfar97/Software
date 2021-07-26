from PyQt5.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar, QLineEdit, QAbstractItemView, QPushButton, QCheckBox, QStyle, QCompleter, QMenu, QAction

from GUI import ROOT, CONNECT, MODIFY, DELETE, run
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.slideshow import Slideshow

AUTOCOMPLETE = r'GUI\autocomplete.txt'

class ManageData(QMainWindow):

    transaction_complete = pyqtSignal()
    window_closed = pyqtSignal()

    def __init__(self, parent=None):
    
        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        # self.create_menu()
        self.showMaximized()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def create_widgets(self):
            
        self.windows = set()
        self.MYSQL = CONNECT()

        self.gallery = Gallery(self)
        self.preview = Preview(self, 'white')
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

        self.transaction_complete.connect(self.select_records)
    
    def create_menu(self):
        
        self.menubar = self.menuBar()
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addWidget(Ribbon(self))
        self.menubar.triggered.connect(self.menuPressEvent)
        self.toolbar.actionTriggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        
        # View
        help = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')

    # @run
    @pyqtSlot()
    def select_records(self, query=None):

        if query is None: query = self.gallery.query

        try:
            record = self.MYSQL.execute(query, fetch=1)
            self.gallery.images.update(record)
        except:
            QMessageBox.information(
                None, 'The database is busy', 
                'There is a transaction currently taking place',
                QMessageBox.Ok
                )
            return 0

        return 1

    # @run
    def update_records(self, indexes, **kwargs):
                
        parameters = []
        random = 'RANDOM()' in self.gallery.get_order()

        for key, vals in kwargs.items():
            
            key = key.lower()
            
            if isinstance(vals, tuple):
                
                for val in vals[0]:

                    parameters.append(f'{key}=CONCAT({key}, " {val} ")')
                
                for val in vals[1]:

                    parameters.append(f'{key}=REPLACE({key}, " {val} ", " ")')
                
            else: parameters.append(f'{key}={vals}')

        if 'Path' in kwargs:

            for path, in indexes:
                path = ROOT / path

                try: path.rename(path.with_name())
                except (
                    FileExistsError, 
                    FileNotFoundError, 
                    PermissionError
                    ) as error:
                    message = QMessageBox.question(
                        None, type(error).__name__, str(error), 
                        QMessageBox.Ignore | QMessageBox.Ok
                        )
                    if message == QMessageBox.Ok: return 0

        busy = self.MYSQL.execute(
            MODIFY.format(', '.join(parameters)), indexes, many=1, commit=1
            )
        if busy:
            QMessageBox.information(
                None, 'The database is busy', 
                'There is a transaction currently taking place',
                QMessageBox.Ok
                )
            return 0

        self.preview.update()
        if not random: self.transaction_complete.emit()
        
        return 1

    # @run    
    def delete_records(self, indexes):
                
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:
            
            random = 'RANDOM()' in self.gallery.get_order()

            paths = [
                (index.data(Qt.UserRole)[0],) for index in indexes 
                ]
            
            busy = self.MYSQL.execute(DELETE, paths, many=1)
            if busy:
                QMessageBox.information(
                    None, 'The database is busy', 
                    'There is a transaction currently taking place',
                    QMessageBox.Ok
                    )
                self.MYSQL.rollback()
                return 0

            for path, in paths: (ROOT / path).unlink(True)
            self.MYSQL.commit()

            self.preview.update()

            if not random: self.transaction_complete.emit()
            else:
                table = self.gallery.images.table
                for index in indexes[::-1]:
                    if index is None: continue
                    del table.images[index.data(300)]

                table.layoutChanged.emit()
                self.gallery.images.clearSelection()
                self.gallery.statusbar(self.gallery.images.total())

            return 1
    
    def start_slideshow(self, index=None):
        
        view = self.gallery.images
        if not view.total(): return

        indexes = view.table.images
        index = index if index else view.currentIndex()
        index = sum(index.data(100))
        slideshow = Slideshow(self, indexes, index)
        
        self.windows.add(slideshow)

    def menuPressEvent(self, action=None):

        print(action)

    def keyPressEvent(self, event):

        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter):
            
            self.start_slideshow()

        elif key_press == Qt.Key_Delete:
            
            gallery = [
                index for index in
                self.gallery.images.selectedIndexes()
                if index.data(300)
                ]
            self.delete_records(gallery)
                        
        elif key_press == Qt.Key_Escape: self.close()
    
        elif self.parent is not None:
            
            self.parent.keyPressEvent(event)

    def closeEvent(self, event):
        
        self.MYSQL.close()
        self.windows.clear()

class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super(Ribbon, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
        
    def configure_gui(self):
         
        self.undo = ['']
        self.redo = []

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def create_widgets(self):
        
        # History navigation
        self.history = QHBoxLayout()
        self.layout.addLayout(self.history)

        self.back = QPushButton()
        self.forward = QPushButton()
        self.menu = QPushButton()
        
        for button, event, icon in zip(
            [self.back, self.forward, self.menu],
            [self.go_back, self.go_forward, self.menu.showMenu],
            [QStyle.SP_ArrowBack, QStyle.SP_ArrowForward, QStyle.SP_ArrowDown]
            ):
            
            button.setIcon(self.style().standardIcon(icon))
            button.clicked.connect(event)
            button.setEnabled(False)
            self.history.addWidget(button)

        # Search function
        self.tags = QLineEdit(self)
        self.tags.setPlaceholderText('Enter tags')
        self.tags.setCompleter(
            QCompleter(open(AUTOCOMPLETE).read().split())
            )
        self.tags.returnPressed.connect(self.parent().select_records)
        self.tags.textChanged.connect(self.parent().gallery.update)
        self.layout.addWidget(self.tags, 6)
        
        self.timer = QTimer(self.tags)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.parent().select_records)
        self.tags.textChanged.connect(lambda: self.timer.start(1000))
        
        self.refresh = QPushButton(self)
        self.refresh.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh.clicked.connect(self.parent().select_records)
        self.layout.addWidget(self.refresh, 1, Qt.AlignLeft)
        
        self.multi = QCheckBox('Multi-selection', self)
        self.multi.clicked.connect(self.changeSelectionMode)
        self.layout.addWidget(self.multi, 0, Qt.AlignLeft)

        self.tags.setFocus()
        
    def update(self, string='', check=1):

        if string:

            if self.undo:
                if string != self.undo[-1]:
                    self.undo.append(string)
                    self.redo.clear()
            else:
                self.undo.append(string)
                self.redo.clear()

        self.back.setEnabled(bool(self.undo[1:]))
        self.forward.setEnabled(bool(self.redo))
        self.menu.setEnabled(bool(self.undo + self.redo))

        menu = QMenu(self, triggered=self.menuEvent)
        for state in reversed(self.undo[1:] + self.redo[::-1]):
            
            action = QAction(state, menu, checkable=True)
            if state == string and check: 
                action.setChecked(True)
                check=0
            menu.addAction(action)

        else: self.menu.setMenu(menu)
        
        self.tags.setText(self.undo[-1])
    
    def go_back(self, event=None, update=True):
        
        if len(self.undo) > 1:
            self.redo.append(self.undo.pop())
            if update: self.update()

    def go_forward(self, event=None, update=True):
        
        if self.redo:
            self.undo.append(self.redo.pop())
            if update: self.update()
    
    def changeSelectionMode(self, event):
        
        if event:
            self.parent().images.setSelectionMode(
                QAbstractItemView.MultiSelection
                )
        else:
            self.parent().images.setSelectionMode(
                QAbstractItemView.ExtendedSelection
                )
            self.parent().images.clearSelection()
    
    def menuEvent(self, event):

        action = event.text()

        if action in self.undo:

            while action != self.undo[-1]: self.go_back(update=False)

        elif action in self.redo:

            while action in self.redo: self.go_forward(update=False)
        
        self.update()

    def keyPressEvent(self, event):
    
        key_press = event.key()

        if key_press in (Qt.Key_Return, Qt.Key_Enter): pass

        else: self.parent().keyPressEvent(event)