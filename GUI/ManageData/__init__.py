'''
Consists of a lefthand gallery of images and a righthand display for selected image. Allows deletion and updating of records, as well as a slideshow function that can display images and videos in fullscreen.
'''
import re
from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox, QStatusBar, QAbstractItemView

from GUI.utils import INSERT, UPDATE, DELETE, COMIC, AUTOCOMPLETE, ENUM, Authenticate, Completer, Worker, update_autocomplete, remove_redundancies, get_path, get_values, copy_to, find_match
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.managedata.ribbonView import Ribbon
from GUI.slideshow import Slideshow

class ManageData(QMainWindow):

    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)
    
    def __init__(self, parent=None, admin=0):
    
        if admin: ENUM['Explicit'] = ''

        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.showMaximized()
        
        authenticator = Authenticate()
        self.mysql = authenticator.success()
        self.mysql.setParent(self)
        self.mysql.finishedTransaction.connect(self.select_records)
        self.mysql.finishedTransaction.connect(self.update_statusbar)
        self.mysql.errorTransaction.connect(
            lambda error: QMessageBox.warning(None, 'Error', str(error))
            )
        self.mysql.finishedSelect.connect(self.gallery.clearSelection)
        self.mysql.finishedSelect.connect(self.gallery.update_gallery)
        self.mysql.finishedSelect.connect(self.update_statusbar)
        self.mysql.finishedSelect.connect(lambda: self.preview.update(None))
        self.mysql.finishedUpdate.connect(self.close_properties)
        self.mysql.finishedDelete.connect(self.delete_records)
        
        if admin:
            
            self.gallery.rating.actions()[0].setChecked(True)
            self.gallery.order[0].actions()[6].setChecked(True)
            self.ribbon.order = {
                'sort': 'ORDER BY RAND()',
                'column': {
                    'rating': 'Explicit',
                    'type': 'All',
                    }
                }
        
    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.layout.setSpacing(0)

    def create_widgets(self):

        self.windows = set()
        self.threadpool = QThreadPool()
        self.query = None

        self.gallery = Gallery(self)
        self.preview = Preview(self)
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(30)

        self.gallery.selection.connect(self.update_gallery)
        self.gallery.selection.connect(self.update_statusbar)
        self.gallery.delete.connect(self.delete_records)
        self.gallery.load_comic.connect(self.read_comic)
        self.gallery.find_artist.connect(self.find_by_artist)
        
        # self.installEventFilter(self)

    def create_menu(self):
        
        self.menubar = self.menuBar()
        self.toolbar = self.addToolBar('Ribbon')

        self.ribbon = Ribbon(self)
        self.toolbar.addWidget(self.ribbon)

        self.menubar.triggered.connect(self.menuPressEvent)
        self.toolbar.actionTriggered.connect(self.menuPressEvent)
        self.ribbon.selection_mode.connect(self.setSelectionMode)
        self.ribbon.query_updated.connect(self.select_records)
        self.gallery.order_updated.connect(self.update_query)
        self.ribbon.tags.setFocus()

        # File
        file = self.menubar.addMenu('File')
        file.addAction('Add image(s)')
        file.addAction(
            'Copy Images to', 'CTRL+SHIFT+C', 
            lambda: copy_to(self, self.gallery.selectedIndexes())
            )
        file.addAction(
            'Find Image', 'CTRL+SHIFT+F', 
            lambda: self.select_records(find_match(self))
            )
        file.addSeparator()
        file.addAction('Exit', 'CTRL+W', self.close)
        
        # database
        database = self.menubar.addMenu('Database')
        database.addAction('Reconnect')
        database.addAction('Current statement')
        database.addAction('Update Autocomplete')
        database.addAction('Remove Redundancies')
        
        # View
        view = self.menubar.addMenu('View')
        
        # Help
        help = self.menubar.addMenu('Help')
    
    def select_records(self, query=None):
        
        if type(query) == str: self.query = query
        
        worker = Worker(self.mysql.execute, self.query)
        self.threadpool.start(worker)
        
        self.preview.update()

    def insert_records(self, indexes):
        
        worker = Worker(self.mysql.execute, INSERT, indexes, many=1)
        self.threadpool.start(worker)
    
    def update_records(self, source, indexes, kwargs):
        
        parameters = []

        for key, vals in kwargs.items():
            
            key = key.lower()
            
            if isinstance(vals, tuple):
                                
                for val in vals[0]:

                    parameters.append(f'{key}=CONCAT({key.lower()}, " {val} ")')
                
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

        if not indexes: return
        
        if isinstance(indexes[0], tuple):

            for path, in indexes: 
                get_path(path).unlink(True)
            self.mysql.cursor.close
            self.mysql.conn.commit()
            self.mysql.conn.close()
            return
        
        paths = [
            (index.data(Qt.ItemDataRole.UserRole)[1],) 
            for index in indexes
            if index.data(Qt.ItemDataRole.FontRole) is not None
            ]
            
        message = QMessageBox.question(
            None, 'Delete', 
            'Are you sure you want to delete this?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
        if message == QMessageBox.StandardButton.Yes:
            
            worker = Worker(self.mysql.execute, DELETE, paths, many=1)
            self.threadpool.start(worker)
            
        return 1
            
    def start_slideshow(self, index=None):
        
        if not self.gallery.total(): return

        indexes = self.gallery.table.images
        index = index if index else self.gallery.currentIndex()
        # slideshow = Slideshow(self, indexes, index.data(Qt.ItemDataRole.FontRole))
        
        # self.windows.add(slideshow)
        
        worker = Worker(Slideshow, (self, indexes, index.data(Qt.ItemDataRole.FontRole)))
        self.threadpool.start(worker)

    def update_query(self, order):
        
        self.ribbon.order = self.gallery.update_order(1)
            
        self.ribbon.update_query()
         
    def update_gallery(self, select, deselect):
        
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

        artist = index.data(Qt.ItemDataRole.UserRole)[2]
        
        if artist:
            
            self.ribbon.setText(' OR '.join(artist.split()))

        else: QMessageBox.information(
            self, 'Find by artist', 'This image has no artist'
            )

    def read_comic(self, event=None):
        
        if event[1] == 1 or (
            re.search('type=.comic', self.query) and 
            not re.search('comic=.+', self.ribbon.text())
            ):
            
            path = event[0].data(Qt.ItemDataRole.UserRole)[1]

            try: 
                
                parent, = self.mysql.execute(COMIC, (path,), fetch=1)[0]
                self.ribbon.setText(f'comic={parent}')
                self.gallery.rating.actions()[0].trigger()
                self.gallery.order[0].actions()[0].trigger()
            
            except IndexError: 
            
                QMessageBox.information(
                    self, 'Comic not found', 
                    f'Path "{path}" returned nothing'
                    )
                
        
        else: self.start_slideshow()
    
    def setSelectionMode(self, event):
        
        if event:
            
            self.gallery.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection
                )
        
        else:
            
            self.gallery.setSelectionMode(
                QAbstractItemView.SelectionMode.ExtendedSelection
                )
            self.gallery.clearSelection()
    
    def close_properties(self, property):
        
        if property is not None: property.close()        
        
    def menuPressEvent(self, event=None):

        match event.text():
        
            # File
            case 'Add image(s)':
                
                QMessageBox.information(
                    self, 'Non-existant function',
                    'That function does not exist'
                    )
                return
                self.insert_records(records)
            
            case 'Exit': self.close()
            
            # Database
            case 'Reconnect':
                
                authenticator = Authenticate()
                self.mysql = authenticator.success()
                self.threadpool.clear()
                self.threadpool = QThreadPool()
            
            case 'Current statement':
                
                QMessageBox.information(
                    self, 'Current Statement', self.query
                    )
                
            case 'Update Autocomplete':

                worker = Worker(update_autocomplete)
                self.threadpool.start(worker)

                with open(AUTOCOMPLETE, encoding='utf8') as file:
                    
                    self.ribbon.tags.setCompleter(
                        Completer(file.read().split())
                        )
                    
            case 'Remove Redundancies':
                
                worker = Worker(remove_redundancies)
                self.threadpool.start(worker)
                
    def mousePressEvent(self, event):
        
        button_press = event.button()
        
        if button_press == Qt.MouseButton.XButton1:
            
            self.ribbon.go_back()
            
        elif button_press == Qt.MouseButton.XButton2:
            
            self.ribbon.go_forward()
               
    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        alt = modifiers == Qt.KeyboardModifier.AltModifier

        if alt:
            
            match key_press:
                
                case Qt.Key.Key_Left: self.ribbon.go_back()
                
                case Qt.Key.Key_Right: self.ribbon.go_forward()
            
                case Qt.Key.Key_F4: self.close()

                case _: self.key_pressed.emit(event)

        match key_press:
            
            case Qt.Key.Key_F4: self.ribbon.tags.setFocus()
            
            case Qt.Key.Key_F5: self.select_records()

            case Qt.Key.Key_Delete:
                
                self.delete_records(self.gallery.selectedIndexes())
                            
            case Qt.Key.Key_Escape: self.close()
            
            case (Qt.Key.Key_Up|Qt.Key.Key_Down|Qt.Key.Key_Right|Qt.Key.Key_Left|Qt.Key.Key_PageUp|Qt.Key.Key_PageDown|Qt.Key.Key_Home|Qt.Key.Key_End|Qt.Key.Key_Return|Qt.Key.Key_Enter):
            
                self.gallery.keyPressEvent(event)

            case _: self.key_pressed.emit(event)
     
    def dragEnterEvent(self, event):
        
        if event.mimeData().hasUrls():
            
            event.accept()
        
        else: event.ignore()
   
    def dropEvent(self, event):
        
        values = (get_values(file) for file in event.mimeData.urls())
        
        return
        self.insert_records()
            
    def closeEvent(self, event):
        
        self.mysql.close()
        self.threadpool.clear()
        for window in self.windows: window.close()
        self.closedWindow.emit(self)