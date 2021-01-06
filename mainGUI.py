from GUI import ROOT, CONNECTION, MODIFY, DELETE
from GUI.galleryView import Gallery
from GUI.previewView import Preview, Timer
from GUI.slideshowView import Slideshow
from GUI.designView import Design
from GUI.datasetView import Dataset
from GUI.trainView import Train

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget,  QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QStatusBar, QGroupBox, QPushButton, QAction, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class App(QMainWindow):
    
    def __init__(self):
        
        super(App, self).__init__()
        self.setWindowTitle('Custom GUI')
        self.configure_gui()
        self.create_widgets()
        self.show()
        
    def configure_gui(self):
        
        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()

        self.setGeometry(
            int(width * .34), int(height * .29),
            int(width * .35), int(height * .48)
            )
        self.frame = QGroupBox()
        self.layout = QVBoxLayout()
        self.frame.setLayout(self.layout) 

        self.layout.setAlignment(Qt.AlignHCenter)
        self.setContentsMargins(10, 10, 10, 15)
        self.frame.setFixedHeight(height // 3)
        self.setCentralWidget(self.frame)
        
    def create_widgets(self):
        
        self.windows = {}
        options = {
            'Manage Data': ManageData, 
            'Gesture Draw': GestureDraw, 
            'Machine Learning': MachineLearning
            }
        for name, app in options.items():
            
            option = QPushButton(name, self)
            option.setStyleSheet('''
                QPushButton::focus:!hover {background: #b0caef};
                text-align: left;
                padding: 25px;
                font: 12px;
                ''')
            option.clicked.connect(
                lambda checked, x=name, y=app: self.select(x, y)
                )
            option.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
                )
            
            self.layout.addWidget(option)
    
    def select(self, title, app):

        self.windows[title] = self.windows.get(title, []) + [app(self)]
        self.hide()
        
    def is_empty(self): return sum(self.windows.values(), [])

    def keyPressEvent(self, event):

        key_press = event.key()
        modifiers = event.modifiers()
        ctrl = modifiers == Qt.ControlModifier

        if ctrl:

            if key_press == Qt.Key_1: self.select('Manage Data', ManageData)

            elif key_press == Qt.Key_2: self.select('Gesture Draw', GestureDraw)

            elif key_press == Qt.Key_3: self.select('Machine Learning', MachineLearning)

        elif key_press in (Qt.Key_Return, Qt.Key_Enter): 
            
            if not self.isHidden(): self.focusWidget().click()

        elif key_press == Qt.Key_Escape: self.close()

    def closeEvent(self, event):
        
        CONNECTION.close()
        Qapp.quit()

class ManageData(QMainWindow):
            
    TYPE = {
        'Photograph': 'エラティカ ニ',
        'Illustration': 'エラティカ 三',
        'Comic': 'エラティカ 四',
        1: 'エラティカ ニ',
        2: 'エラティカ 三',
        3: 'エラティカ 四'
        }

    def __init__(self, parent):
        
        super(ManageData, self).__init__()
        self.setWindowTitle('Manage Data')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.showMaximized()
        self.gallery.populate()

    def configure_gui(self):
        
        self.center = QWidget(self)
        self.layout = QHBoxLayout()

        self.center.setLayout(self.layout)
        self.setCentralWidget(self.center)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width, height)

    def create_widgets(self):
            
        self.gallery = Gallery(self)
        self.preview = Preview(self, 'white')
        self.slideshow = Slideshow(self)
        
        self.layout.addWidget(self.gallery)
        self.layout.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)
    
    def start_slideshow(self, index=None):

        view = self.gallery.images
        self.slideshow.gallery = view.table.images
        
        index = index if index else view.currentIndex()
        try: self.slideshow.index = sum(index.data(100))
        except: return
        
        self.slideshow.move(0)
        if self.slideshow.isHidden():
            self.slideshow.showMaximized()
        self.slideshow.activateWindow()

    def change_records(self, gallery, **kwargs):
        
        parameters = []

        for key, vals in kwargs.items():
            
            if isinstance(vals, tuple):
                
                for val in vals[0]:
                    parameters.append(
                        f'{key}=CONCAT({key}, "{val} ")'
                        )
                for val in vals[1]:
                    parameters.append(
                        f'{key}=REPLACE({key}, " {val} ", " ")'
                        )
                
            else: parameters.append(f'{key}={vals}')
                
        if 'Type' in kwargs:
            
            for path, in gallery:
                path = ROOT / path
                dropbox = path.parent.parent
                new = self.TYPE[kwargs['Type']]

                try: path.rename(dropbox / new / path.name)
                except PermissionError as error:
                    message = QMessageBox.question(
                        self, 'Permission Error', 
                        str(error), QMessageBox.Ok
                        )
                    return 0
        CONNECTION.execute(
            MODIFY.format(', '.join(parameters)), gallery, many=1, commit=1
            )
        self.gallery.populate()
        return 1
    
    def delete_records(self, event=None):
        
        message = QMessageBox.question(
            self, 'Delete', 'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes:

            gallery = [
                (index.data(Qt.UserRole),) for index in 
                self.gallery.images.selectedIndexes() 
                ]
            for path, in gallery: 
                try: (ROOT / path).unlink()
                except (FileNotFoundError, TypeError): pass
                    
            CONNECTION.execute(DELETE, gallery, many=1, commit=1)
            
            self.gallery.images.update([])
            self.gallery.populate()
    
    def keyPressEvent(self, event):

        key_press = event.key()

        if key_press == Qt.Key_Return: self.start_slideshow()

        elif key_press == Qt.Key_Delete: self.delete_records()
                        
        elif key_press == Qt.Key_Escape: self.close()
    
        else: self.parent.keyPressEvent(event)

    def closeEvent(self, event):
        
        self.slideshow.close()
        try: self.parent.windows[self.windowTitle()].remove(self)
        except: pass
        if not self.parent.is_empty(): self.parent.show()
 
class GestureDraw(QMainWindow):
    
    def __init__(self, parent):
        
        super(GestureDraw, self).__init__()
        self.setWindowTitle('Gesture Draw')
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.show()
        self.gallery.populate()

    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)  
        self.stack.setContentsMargins(0, 0, 5, 0)

        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width // 2, height)

    def create_widgets(self):
        
        self.gallery = Gallery(self)
        self.preview = Preview(self, 'black')
        self.timer = Timer(self.preview)
     
        self.stack.addWidget(self.gallery)
        self.stack.addWidget(self.preview)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(25)
        
    def start_session(self):
        
        gallery = (
            thumb.data(Qt.UserRole) for thumb in 
            self.gallery.images.selectedIndexes()
            )
        time = self.gallery.ribbon.time.text()
        
        if gallery and time:

            self.statusbar.hide()

            if ':' in time:
                min, sec = time.split(':')
                time = (int(min) * 60) + int(sec)
            else: time = int(time)
            
            self.stack.setCurrentIndex(1)
            self.timer.start(gallery, time)
   
    def keyPressEvent(self, event):
        
        key_press = event.key()

        if key_press == Qt.Key_Return: self.start_session()

        elif key_press == Qt.Key_Space: self.timer.pause()

        elif key_press == Qt.Key_Escape:

            if self.stack.currentIndex():
                
                self.statusbar.show()
                self.statusbar.showMessage('')
                self.stack.setCurrentIndex(0)
                self.gallery.populate()
                            
            else: self.close()
        
        else: self.parent.keyPressEvent(event)

    def closeEvent(self, event):
    
        self.parent.windows[self.windowTitle()].remove(self)
        if not self.parent.is_empty(): self.parent.show()
 
class MachineLearning(QMainWindow):
    
    def __init__(self, parent):
        
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
        # self.stack.setContentsMargins(0, 0, 5, 0)

        resolution = Qapp.desktop().screenGeometry()
        width, height = resolution.width(),  resolution.height()
        self.setGeometry(0, 0, width, height)

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

    def menuAction(self, action):

        print(action)

    def keyPressEvent(self, event):
        
        key_press = event.key()
                
        if key_press == Qt.Key_Escape: self.close()

    def closeEvent(self, event):
        
        self.parent.windows[self.windowTitle()].remove(self)
        if not self.parent.is_empty(): self.parent.show()

Qapp = QApplication([])
app = App()
Qapp.setQuitOnLastWindowClosed(False)

Qapp.exec_()