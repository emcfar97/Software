from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QStackedWidget, QMessageBox, QStatusBar, QGroupBox, QPushButton, QInputDialog, QSizePolicy, QAbstractItemView

from GUI.utils import AUTOCOMPLETE, Worker, Timer, Authenticate, update_autocomplete, remove_redundancies, copy_to, create_submenu
from GUI.managedata import ManageData
from GUI.managedata.galleryView import Gallery
from GUI.managedata.previewView import Preview
from GUI.managedata.ribbonView import Ribbon
from GUI.deeplearning import DeepLearning
from GUI.videosplitter import VideoSplitter

GESTURE = {
    '30 seconds': '30', 
    '1 minute': '60', 
    '2 minutes': '120', 
    '5 minutes': '300', 
    'Custom Time': None
    }

class App(QMainWindow):

    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.show()

    def configure_gui(self):
        
        resolution = self.screen().size()
        width, height = resolution.width(),  resolution.height()

        self.setGeometry(
            int(width * .34), int(height * .29),
            int(width * .35), int(height * .48)
            )
        self.frame = QGroupBox()
        self.layout = QVBoxLayout()
        self.frame.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setContentsMargins(10, 10, 10, 15)
        self.frame.setFixedHeight(height // 3)
        self.setCentralWidget(self.frame)
        
    def create_widgets(self):
        
        self.windows = {}
        options = {
            'Manage Data': ManageData, 
            'Gesture Draw': GestureDraw, 
            'Machine Learning': DeepLearning,
            'Video Splitter': VideoSplitter,
            }
            
        for name, app in options.items():
            
            option = QPushButton(name, self)
            option.setStyleSheet('''
                QPushButton::focus:!hover {background: #b0caef};
                text-align: left;
                padding: 20px;
                font: 12px;
                ''')
            option.clicked.connect(
                lambda checked, x=name, y=app: self.select(x, y)
                )
            option.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                )
            
            self.layout.addWidget(option)
    
    def create_menu(self): pass

    def select(self, title, app):
        
        app = app(self)
        app.closedWindow.connect(self.closed_window)
        app.key_pressed.connect(self.keyPressEvent)
        self.windows[title] = self.windows.get(title, []) + [app]
        self.hide()

    def closed_window(self, event):

        self.windows[event.windowTitle()].remove(event)
        if not any(self.windows.values()): self.show()

    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        ctrl = modifiers == Qt.KeyboardModifier.ControlModifier
        num = event.modifiers() == Qt.KeyboardModifier.KeypadModifier

        if ctrl:
            
            match key_press:
                
                case Qt.Key.Key_1: self.select('Manage Data', ManageData)

                case Qt.Key.Key_2: self.select('Gesture Draw', GestureDraw)

                case Qt.Key.Key_3: self.select('Machine Learning', DeepLearning)
                
                case Qt.Key.Key_4: self.select('Video Splitter', VideoSplitter)

        match key_press:
            
            case (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            
                if not self.isHidden(): self.focusWidget().click()

            case Qt.Key.Key_Escape: self.close()

    def closeEvent(self, event): QApplication.quit()

class GestureDraw(QMainWindow):

    closedWindow = pyqtSignal(object)
    key_pressed = pyqtSignal(object)

    def __init__(self, parent, *args):
        
        super(App, self).__init__()
        self.setWindowTitle('Gesture Draw')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.create_menu()
        self.ribbon.order = {
            'sort': 'ORDER BY RAND()',
            'column': {
                'rating': 'Explicit',
                'type': 'All',
                }
            }
        self.show()

        authenticator = Authenticate()
        self.mysql = authenticator.success()
        self.mysql.finishedTransaction.connect(self.select_records)
        self.mysql.finishedTransaction.connect(self.update_statusbar)
        self.mysql.errorTransaction.connect(
            lambda error: QMessageBox.warning(None, 'Error', str(error))
            )
        self.mysql.finishedSelect.connect(self.update_statusbar)
        self.mysql.finishedSelect.connect(self.gallery.clearSelection)
        self.mysql.finishedSelect.connect(self.gallery.update_gallery)
        self.mysql.finishedSelect.connect(lambda: self.preview.update(None))
        
        self.ribbon.refresh.click()
        
    def configure_gui(self):

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)  

        resolution = self.geometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width // 2, height)

    def create_widgets(self):

        self.windows = set()
        self.threadpool = QThreadPool()
        self.query = None

        self.gallery = Gallery(self)
        self.preview = Preview(self)
        self.timer = Timer(self.preview, self)
        
        self.stack.addWidget(self.gallery)
        self.stack.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(30)
        # self.installEventFilter(self)

        self.gallery.selection.connect(self.update_statusbar)
        self.gallery.find_artist.connect(self.find_by_artist)
        self.gallery.setContentsMargins(5, 0, 0, 0)
        
        for action in self.gallery.menu.actions():
            
            if action.text() in ['Delete', 'Properties']:
                
                self.gallery.menu.removeAction(action)
                
        self.preview.label.setStyleSheet(f'background: black')

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
        self.ribbon.multi.click()
        self.ribbon.tags.setFocus()

        # File
        file = self.menubar.addMenu('File')
        file.addAction(
            'Copy Images to', 'CTRL+SHIFT+C', 
            lambda: copy_to(self, self.gallery.selectedIndexes())
            )
        self.gesture_menu = create_submenu(
            file, 'Gesture Draw', GESTURE.keys(), check=False, get_menu=True
            )[1]
        file.addMenu(self.gesture_menu)
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
    
    def select_records(self):
        
        if type(query) == str: self.query = query
        
        worker = Worker(self.mysql.execute, self.query)
        self.threadpool.start(worker)
        
        self.preview.update()

    def start_session(self, gallery, time):
        
        if gallery and time:

            self.menubar.hide()
            self.toolbar.hide()
            self.statusbar.hide()

            if ':' in time:
                
                min, sec = time.split(':')
                time = (int(min) * 60) + int(sec)
                
            else: time = int(time)
            
            self.stack.setCurrentIndex(1)
            self.timer.start(gallery, time)
        
        else:
            
            QMessageBox.information(
                self, '', 
                'You are either missing images or a time',
                QMessageBox.StandardButton.Ok
                )

    def update_query(self, order):
        
        self.ribbon.order = self.gallery.update_order(mode=1)
            
        self.ribbon.update_query(gesture=True)
         
    def update(self, select, deselect):
        
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
    
    def menuPressEvent(self, event=None):

        match event.text():
        
            # File
            case GESTURE.keys():
                
                if event.text() == 'Custom Time':
                    
                    time, ok = QInputDialog.getText(
                        self, "Dialog", "Enter time:"
                        )
                
                    if ok:
                        
                        gallery = self.gallery.selectedIndexes()
                        self.start_session(gallery, time)
                        
                else:
                    
                    gallery = self.gallery.selectedIndexes()
                    self.start_session(gallery, GESTURE[event.text()])

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

                self.ribbon.tags.setCompleter(
                    QCompleter(open(AUTOCOMPLETE).read().split())
                    )

            case 'Remove Redundancies':
                
                worker = Worker(remove_redundancies)
                self.threadpool.start(worker)
        
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
        
    def closeEvent(self, event):
        
        self.mysql.close()
        self.threadpool.clear()
        for window in self.windows: window.close()
        self.closedWindow.emit(self)