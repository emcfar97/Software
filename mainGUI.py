from os import remove
from subprocess import Popen
from GUI import ROOT, CONNECTION, MODIFY, DELETE, NEZUMI
from GUI.galleryView import Gallery
from GUI.previewView import Preview, Timer
from GUI.sliderView import Slideshow

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGroupBox,  QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QStatusBar, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt

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
                padding: 25px;
                font: 12px;
                text-align: left;
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

    def keyPressEvent(self, sender):

        key_press = sender.key()
        modifiers = sender.modifiers()
        ctrl = modifiers == Qt.ControlModifier

        if ctrl:

            if key_press == Qt.Key_1: self.select('Manage Data', ManageData)

            elif key_press == Qt.Key_2: self.select('Gesture Draw', GestureDraw)

        elif key_press == Qt.Key_Return: self.focusWidget().click()

        elif key_press == Qt.Key_Escape: self.close()

    def closeEvent(self, sender):
        
        CONNECTION.close()
        Qapp.quit()

class ManageData(QMainWindow):
            
    TYPE = [
        None,
        'エラティカ ニ',
        'エラティカ 三'
        ]

    def __init__(self, parent):
        
        super(ManageData, self).__init__(parent)
        self.setWindowTitle('Manage Data')
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
        self.statusbar.setFixedHeight(30)
    
    def start_slideshow(self, index=None):

        view = self.gallery.images
        self.slideshow.gallery = view.table.images
        
        index = index if index else view.currentIndex()
        try: self.slideshow.index = sum(index.data(100))
        except: return
        
        self.slideshow.move(0)
        self.slideshow.showMaximized()

    def change_records(self, gallery, *args):
        
        parameters = []
        tags, artists, stars, rating, type_ = args

        if tags:
            for tag in tags[0]:
                parameters.append(f'tags=CONCAT(tags, "{tag} ")')
            for tag in tags[1]:
                parameters.append(f'tags=REPLACE(tags, " {tag} ", " ")')

        if artists:
            for artist in artists[0]:
                parameters.append(f'artist=CONCAT(artist, "{artist} ")')
            for artist in artists[1]:
                parameters.append(f'artist=REPLACE(artist, " {artist} ", " ")')

        if stars: parameters.append(f'stars={stars}')
        if rating: parameters.append(f'rating={rating}')
        if type_: 
            parameters.append(f'type={type_}')
            # for path, in gallery:
            #     path = ROOT / path
            #     old, new = path.parts[5], self.TYPE[type_]
            #     path.rename(path.parent.parent / new / path.name)
            # parameters.append(f'path=REPACE(path, {old}, {new})')

        CONNECTION.execute(
            MODIFY.format(', '.join(parameters)), gallery, many=1, commit=1
            )
        self.gallery.populate()
    
    def delete_records(self, sender=None):
        
        message = QMessageBox.question(
            self, 'Delete', 'Are you sure you want to delete this?',
            QMessageBox.Yes | QMessageBox.No
            )
        
        if message == QMessageBox.Yes: 

            gallery = gallery = [
                (index.data(Qt.UserRole),) for index in 
                self.gallery.images.selectedIndexes()
                ]
            for path, in gallery: 
                try: remove(path)
                except PermissionError: return
                except FileNotFoundError: pass
                except TypeError: pass
            CONNECTION.execute(DELETE, gallery, many=1, commit=1)
            self.gallery.populate()
    
    def keyPressEvent(self, sender):

        key_press = sender.key()

        if key_press == Qt.Key_Return: self.start_slideshow()

        elif key_press == Qt.Key_Delete: self.delete_records()
                        
        elif key_press == Qt.Key_Escape: self.close()
    
        else: self.parent().keyPressEvent(sender)

    def closeEvent(self, sender):

        self.slideshow.close()
        self.parent().windows[self.windowTitle()].remove(self)
        if not self.parent().is_empty(): self.parent().show()
 
class GestureDraw(QMainWindow):
    
    def __init__(self, parent):
        
        super(GestureDraw, self).__init__(parent)
        self.setWindowTitle('Gesture Draw')
        self.configure_gui()
        self.create_widgets()
        self.show()
        self.gallery.populate()
        Popen([NEZUMI])

    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)  
        self.stack.setContentsMargins(0, 0, 0, 0)

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
        self.statusbar.setFixedHeight(30)
        
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
   
    def keyPressEvent(self, sender):
        
        key_press = sender.key()

        if key_press == Qt.Key_Return: self.start_session()

        elif key_press == Qt.Key_Space: self.timer.pause()

        elif key_press == Qt.Key_Escape:

            if self.stack.currentIndex():
                
                self.statusbar.showMessage('')
                self.stack.setCurrentIndex(0)
                self.gallery.populate()
                self.statusbar.show()
                            
            else: self.close()
        
        else: self.parent().keyPressEvent(sender)

    def closeEvent(self, sender):
    
        self.parent().windows[self.windowTitle()].remove(self)
        if not self.parent().is_empty(): self.parent().show()
 
class MachineLearning(QMainWindow):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        self.setWindowTitle('Machine Learning')
        self.configure_gui()
        self.create_widgets()
        self.showMaximized()

    def configure_gui(self):
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        resolution = Qapp.desktop().screenGeometry()
        self.setGeometry(
            0, 0, 
            resolution.width(),  resolution.height()
            )  

    def create_widgets(self):
        
        self.main = mainView.Main(self)
        self.train = trainView.Training(self)
        
        self.stack.addWidget(self.main)
        self.stack.addWidget(self.train)
        self.stack.setCurrentIndex(1)
        
    def keyPressEvent(self, sender):
                
        if sender.key() == Qt.Key_Escape: self.close()

    def closeEvent(self, sender):
    
        self.close()
        self.parent().show()

Qapp = QApplication([])

app = App()
Qapp.setQuitOnLastWindowClosed(False)

Qapp.exec_()
