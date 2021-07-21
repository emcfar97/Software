from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar
from PyQt5.QtCore import Qt

from GUI import ROOT, CONNECT, MODIFY, DELETE
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.slideshow import Slideshow

class ManageData(QMainWindow):

    def __init__(self, parent=None):
    
        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.MYSQL = CONNECT()
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.showMaximized()
        self.gallery.populate()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def create_widgets(self):
            
        self.windows = set()
        self.gallery = Gallery(self)
        self.preview = Preview(self, 'white')
        
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)
    
    def create_menu(self):
        
        self.menubar = self.menuBar()
        
        # file = self.menubar.addMenu('File')
        
    def start_slideshow(self, index=None):
        
        view = self.gallery.images
        if not view.table.images: return

        indexes = view.table.images
        index = index if index else view.currentIndex()
        index = sum(index.data(100))
        slideshow = Slideshow(self, indexes, index)
        
        self.windows.add(slideshow)

    def select_records(self, statement=None):

        if statement is None:

            statement = self.gallery.statement

        busy = self.MYSQL.execute(statement)
        if busy:
            QMessageBox.information(
                None, 'The database is busy', 
                'There is a transaction currently taking place',
                QMessageBox.Ok
                )
            return 0

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
        if not random: self.gallery.populate()
        
        return 1
    
    def delete_records(self, indexes):
                
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:
            
            paths = [
                (index.data(Qt.UserRole),) for index in indexes 
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
            
            table = self.gallery.images.table
            for index in indexes[::-1]:
                if index is None: continue
                del table.images[index.data(300)]

            table.layoutChanged.emit()
            self.gallery.images.clearSelection()
            self.gallery.statusbar(self.gallery.images.total())

            return 1
    
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