import re
from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar, QAbstractItemView

from GUI import ROOT, CONNECT, UPDATE, DELETE, COMIC, AUTOCOMPLETE, Worker, Completer, update_autocomplete, remove_redundancies, copy_to
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.managedata.ribbonView import Ribbon
from GUI.slideshow import Slideshow

class ManageData(QMainWindow):

    populateGallery = pyqtSignal()
    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)

    def __init__(self, parent=None):
    
        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
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
        self.mysql = CONNECT(self)
        self.threadpool = QThreadPool()

        self.gallery = Gallery(self)
        self.preview = Preview(self)
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(30)

        self.mysql.finishedTransaction.connect(self.select_records)
        self.mysql.finishedSelect.connect(lambda x: self.preview.update(None))
        self.mysql.finishedSelect.connect(self.gallery.clearSelection)
        self.mysql.finishedSelect.connect(self.gallery.update)
        self.mysql.finishedSelect.connect(self.update_statusbar)
        self.mysql.finishedUpdate.connect(lambda x: self.windows.discard(x))
        self.mysql.finishedDelete.connect(self.delete_records)

        self.gallery.selection.connect(self.update_preview)
        self.gallery.selection.connect(self.update_statusbar)
        self.gallery.delete.connect(self.delete_records)
        self.gallery.load_comic.connect(self.read_comic)
        self.gallery.find_artist.connect(self.find_by_artist)

    def create_menu(self):
        
        self.menubar = self.menuBar()
        self.toolbar = self.addToolBar('Ribbon')

        self.ribbon = Ribbon(self)
        self.toolbar.addWidget(self.ribbon)

        self.menubar.triggered.connect(self.menuPressEvent)
        self.toolbar.actionTriggered.connect(self.menuPressEvent)
        self.ribbon.selection_mode.connect(self.setSelectionMode)
        self.ribbon.tags.setFocus()
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction('Add image(s)')
        file.addAction('Update Autocomplete')
        file.addAction('Remove Redundancies')
        file.addAction('Copy Images to')
        file.addSeparator()
        file.addAction('Exit')
        
        # database
        database = self.menubar.addMenu('Database')
        database.addAction('Reconnect')
        database.addAction('Current statement')
        
        # View
        view = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')

    @pyqtSlot()
    def select_records(self):
        
        worker = Worker(self.mysql.execute, self.ribbon.update_query())
        self.threadpool.start(worker)
        
    def update_records(self, source, indexes, kwargs):
        
        parameters = []

        for key, vals in kwargs.items():
            
            key = key.lower()
            
            if isinstance(vals, tuple):
                
                for val in vals[0]:

                    parameters.append(f'{key}=CONCAT({key}, " {val.lower()} ")')
                
                for val in vals[1]:

                    parameters.append(f'{key}=REPLACE({key}, " {val.lower()} ", " ")')
                
            else: parameters.append(f'{key}={vals}')
        
        worker = Worker(
            self.mysql.execute, 
            UPDATE.format(', '.join(parameters)), 
            indexes, many=1, source=source
            )
        self.threadpool.start(worker)
        
    def delete_records(self, indexes):

        if isinstance(indexes[0], tuple):

            for path, in indexes: (ROOT / path).unlink(True)
            self.mysql.cursor.close
            self.mysql.conn.commit()
            self.mysql.conn.close()
            return
        
        paths = [
            (index.data(Qt.UserRole)[0],) 
            for index in indexes
            if index.data(300) is not None
            ]
            
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:
            
            worker = Worker(self.mysql.execute, DELETE, paths, many=1)
            self.threadpool.start(worker)
            
    def start_slideshow(self, index=None):
        
        if not self.gallery.total(): return

        indexes = self.gallery.table.images
        index = index if index else self.gallery.currentIndex()
        index = sum(index.data(100))
        slideshow = Slideshow(self, indexes, index)
        
        self.windows.add(slideshow)

    def update_preview(self, select, deselect):
        
        if self.gallery.total():
            
            if select := select.indexes(): image = select[0]
            
            elif indexes := self.gallery.selectedIndexes():
                image = min(indexes)
            
            else: image = None

            self.preview.update(image)
            
    def update_statusbar(self):
        
        total = self.gallery.total()
        select = len(self.gallery.selectedIndexes())

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
                
        else: select = ''
        
        self.statusbar.showMessage(f'   {total}     {select}')
    
    def find_by_artist(self, index):

        artist = index.data(Qt.UserRole)[1]
        
        if artist: 
            
            self.ribbon.setText(' OR '.join(artist.split()))

        else: QMessageBox.information(
            self, 'Find by artist', 'This image has no artist'
            )

    def read_comic(self, event):
        
        if event[1] == 1 or (
            re.search('type=.comic', self.ribbon.query) and 
            not re.search('comic=.+', self.ribbon.text())
            ):
            
            path = event[0].data(Qt.UserRole)[0]
            parent_, = self.mysql.execute(COMIC, (path,), fetch=1)[0]
            self.ribbon.setText(f'comic={parent_}')
            
            self.rating.actions()[0].trigger()
            self.order[0].actions()[0].trigger()
        
        else: self.start_slideshow()
    
    def setSelectionMode(self, event):
        
        if event:
            self.gallery.setSelectionMode(
                QAbstractItemView.MultiSelection
                )
        else:
            self.gallery.setSelectionMode(
                QAbstractItemView.ExtendedSelection
                )
            self.gallery.clearSelection()
    
    def menuPressEvent(self, event=None):

        action = event.text()
        
        # File
        if action == 'Add image(s)':
            
            QMessageBox.information(self, 'Non existant function', 'That function does not exist')
        
        elif action == 'Update Autocomplete':

            worker = Worker(update_autocomplete)
            self.threadpool.start(worker)

            self.ribbon.tags.setCompleter(
                Completer(open(AUTOCOMPLETE).read().split())
                )

        elif action == 'Remove Redundancies':
            
            worker = Worker(remove_redundancies)
            self.threadpool.start(worker)
        
        elif action == 'Copy Images to':
            
            copy_to(self, self.gallery.selectedIndexes())

        elif action == 'Exit': self.close()
        
        # Database
        elif action == 'Reconnect':
            
            self.mysql = CONNECT(self)
            self.threadpool = QThreadPool()
        
        elif action == 'Current statement':
            
            QMessageBox.information(self, 'Current Statement', self.ribbon.query)
            
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

        elif key_press in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End, Qt.Key_Return, Qt.Key_Enter):
            
            self.gallery.keyPressEvent(event)
            
        else: self.key_pressed.emit(event)
            
    def closeEvent(self, event):
        
        self.threadpool.clear()
        for window in self.windows: window.close()
        self.mysql.close()
        self.closedWindow.emit(self)