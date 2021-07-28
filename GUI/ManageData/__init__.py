from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar

from GUI import ROOT, CONNECT, MODIFY, DELETE, run
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.managedata.ribbonView import Ribbon
from GUI.slideshow import Slideshow

class ManageData(QMainWindow):

    transaction_complete = pyqtSignal()
    window_closed = pyqtSignal()

    def __init__(self, parent=None):
    
        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.parent = parent
        self.configure_gui()
        self.create_menu()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(5, 0, 0, 0)
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

        self.ribbon = Ribbon(self)
        self.toolbar.addWidget(self.ribbon)

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
    def select_records(self):

        self.ribbon.update_query()
        query = self.ribbon.query
        
        try:
            record = self.MYSQL.execute(query, fetch=1)
            self.gallery.update(record)
        except:
            QMessageBox.information(
                None, 'The database is busy', 
                'There is a transaction currently taking place',
                QMessageBox.Ok
                )
            return 0

        return 1

    @run
    def update_records(self, indexes, **kwargs):
        
        parameters = []

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
        self.transaction_complete.emit()
        
    @run
    def delete_records(self, indexes):
                
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:
            
            paths = [
                (index.data(Qt.UserRole)[0],) 
                for index in indexes if index.data(300)
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
            self.transaction_complete.emit()
    
    def start_slideshow(self, index=None):
        
        if not self.gallery.total(): return

        indexes = self.gallery.table.images
        index = index if index else self.gallery.currentIndex()
        index = sum(index.data(100))
        slideshow = Slideshow(self, indexes, index)
        
        self.windows.add(slideshow)

    def update_statusbar(self, total=0, select=''):
         
        total = (
            f'{total} image' 
            if (total == 1) else 
            f'{total} images'
            )

        if select:
            select = (
                f'{select} image selected' 
                if (select == 1) else 
                f'{select} images selected'
                )
        
        self.statusbar.showMessage(f'   {total}     {select}')
    
    def menuPressEvent(self, action=None):

        print(action)

    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        alt = modifiers == Qt.AltModifier

        if alt:
            
            if key_press == Qt.Key_Left: self.ribbon.go_back()
                
            elif key_press == Qt.Key_Right: self.ribbon.go_forward()
            
        if key_press == Qt.Key_F4: self.ribbon.tags.setFocus()
        
        elif key_press == Qt.Key_F5: self.select_records()

        elif key_press == Qt.Key_Delete:
            
            self.delete_records(self.gallery.selectedIndexes())
                        
        elif key_press == Qt.Key_Escape: self.close()
    
        elif self.parent is not None:
            
            self.parent.keyPressEvent(event)

    def closeEvent(self, event):
        
        self.MYSQL.close()
        self.windows.clear()
        self.window_closed.emit()