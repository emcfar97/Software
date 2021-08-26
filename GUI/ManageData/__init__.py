import re
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar, QAbstractItemView

from GUI import ROOT, CONNECT, MODIFY, DELETE, COMIC, AUTOCOMPLETE, Completer, update_autocomplete, remove_redundancies
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.managedata.ribbonView import Ribbon
from GUI.slideshow import Slideshow

class ManageData(QMainWindow):

    populateGallery = pyqtSignal()
    completedTransaction = pyqtSignal(list, int)
    closedWindow = pyqtSignal()

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
        self.mysql = CONNECT()

        self.gallery = Gallery(self)
        self.preview = Preview(self, 'white')
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)

        self.mysql.finishedTransaction.connect(self.select_records)
        self.mysql.finishedSelect.connect(lambda x: self.preview.update(None))
        self.mysql.finishedSelect.connect(self.gallery.clearSelection)
        self.mysql.finishedSelect.connect(self.gallery.update)
        self.mysql.finishedSelect.connect(self.update_statusbar)
        self.mysql.finishedDelete.connect(self.delete_records)

        self.gallery.selection.connect(self.update_preview)
        self.gallery.selection.connect(self.update_statusbar)
        self.gallery.delete_.connect(self.delete_records)
        self.gallery.load_comic.connect(self.read_comic)
        self.gallery.find_artist.connect(self.find_by_artist)

        self.ribbon.selection_mode.connect(self.setSelectionMode)
    
    def create_menu(self):
        
        self.menubar = self.menuBar()
        self.toolbar = self.addToolBar('Toolbar')

        self.ribbon = Ribbon(self)
        self.toolbar.addWidget(self.ribbon)

        self.menubar.triggered.connect(self.menuPressEvent)
        self.toolbar.actionTriggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction('Update Autocomplete')
        file.addAction('Remove Redundancies')
        
        # View
        help = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')

    @pyqtSlot()
    def select_records(self):
        
        self.mysql.execute(self.ribbon.update_query())

    def update_records(self, indexes, source, **kwargs):
        
        parameters = []

        for key, vals in kwargs.items():
            
            key = key.lower()
            
            if isinstance(vals, tuple):
                
                for val in vals[0]:

                    parameters.append(f'{key}=CONCAT({key}, " {val} ")')
                
                for val in vals[1]:

                    parameters.append(f'{key}=REPLACE({key}, " {val} ", " ")')
                
            else: parameters.append(f'{key}={vals}')

        return self.mysql.execute(
            MODIFY.format(', '.join(parameters)), indexes, many=1
            )

    def delete_records(self, indexes, type_=0):

        if isinstance(indexes[0], str):
                        
            for path, in indexes: (ROOT / path).unlink(True)

            self.mysql.commit()
            self.mysql.finished.emit(1)
            
            return
        
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:
            
            paths = [
                (index.data(Qt.UserRole)[0],) 
                for index in indexes
                if index.data(300) is not None
                ]
            
            if self.mysql.execute(DELETE, paths, many=1):
                
                self.mysql.finishedDelete(paths)

    def start_slideshow(self, index=None):
        
        if not self.gallery.total(): return

        indexes = self.gallery.table.images
        index = index if index else self.gallery.currentIndex()
        index = sum(index.data(100))
        slideshow = Slideshow(self, indexes, index)
        
        self.windows.add(slideshow)

    def update_preview(self, select, deselect):
        
        if total := self.gallery.total():
            
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
    
    def find_by_artist(self, event=None):

        index = self.gallery.currentIndex()
        artist = index.data(Qt.UserRole)[1]
        
        if artist: 
            
            self.ribbon.setText(' OR '.join(artist.split()))

        else: QMessageBox.information(
            self, 'Find by artist', 'This image has no artist'
            )

    def read_comic(self, event=None):
        
        if re.search('type=.comic.', self.ribbon.query):
            
            path = self.gallery.currentIndex().data(Qt.UserRole)[0]
            parent_, = self.mysql.execute(COMIC, (path,), fetch=1)[0]
            self.ribbon.setText(f'comic={parent_}')
        
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
        
        if action == 'Update Autocomplete':

            update_autocomplete()
            self.ribbon.tags.setCompleter(
                Completer(open(AUTOCOMPLETE).read().split())
                )

        if action == 'Remove Redundancies':

            remove_redundancies()

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
        
        self.mysql.close()
        self.windows.clear()
        self.closedWindow.emit()