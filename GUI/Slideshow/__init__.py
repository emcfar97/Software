from pathlib import Path
from qute.utilities.menus import menuFromDictionary
from .. import ROOT, create_submenu_, get_frame, copy_to
from ..propertiesView import Properties
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtCore import Qt, QTimer, QStringListModel, QVariant
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QAction

from GUI.slideshow.imageViewer import imageViewer
from GUI.slideshow.videoPlayer import videoPlayer

MENU = {
    'Fullscreen': None,
    'Sep1': None,
    'Slideshow': None,
    'Sep2': None,
    'Rotate right': None,
    'Rotate left': None,
    'Sep3': None,
    'Copy': None,
    'Delete': None,
    'Sep4': None,
    'Properties': None
    }
SLIDESHOW = [
    ['Pause', 'Play', 0], 
    None, 
    ['Speed - Slow', 'Speed - Medium', 'Speed - Fast', 1]
    ]

class Slideshow(QMainWindow):
    
    def __init__(self, parent=None, gallery=list(), index=0):
        
        super(Slideshow, self).__init__()
        self.parent = parent
        self.configure_gui()
        self.create_widgets(gallery)
        self.create_menu()
        self.index = index
        self.move()
        self.showMaximized()
        self.activateWindow()
    
    def configure_gui(self):
        
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.setMouseTracking(True)
        
    def create_widgets(self, gallery):
        
        self.model = Model(self, gallery)

        self.image = imageViewer(self)
        self.video = videoPlayer(self)
        self.stack.addWidget(self.image)
        self.stack.addWidget(self.video)
        
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.BlankCursor)
            )
        
        # self.video.player.mediaStatusChanged.connect(lambda: self.move(+1))
        self.slideshow = QTimer()
        self.slideshow.timeout.connect(
            lambda: self.move(+1)
            )
        
    def create_menu(self):

        self.menubar = self.menuBar()
        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction('Copy Image to',  lambda: copy_to(self, [self.model.index(self.index)]), shortcut='CTRL+SHIFT+C')
        file.addSeparator()
        file.addAction('Exit', self.close, shortcut='Ctrl+W')
        
        # View
        view = self.menubar.addMenu('View')
        view.addAction('Fullscreen', self.fullscreen, shortcut='F11')
        
        # Help
        help = self.menubar.addMenu('Help')
        
        self.fullAction = QAction('Fullscreen', triggered=self.fullscreen)
        
        MENU['Fullscreen'] = self.fullAction
        MENU['Slideshow'] = create_submenu_(
            self, 'Slideshow', SLIDESHOW, self.playEvent
            )[0]
        MENU['Rotate right'] = lambda: self.rotate(+1)
        MENU['Rotate left'] = lambda: self.rotate(-1)
        MENU['Copy'] = self.copy
        MENU['Delete'] = self.delete
        if self.parent is not None: 
            MENU['Properties'] = self.openEditor
        
        self.menu = menuFromDictionary(MENU, self)
        self.menu.insertSeparator(self.menu.children()[1])
        self.menu.insertMenu(self.menu.children()[1], MENU['Slideshow'])
        MENU['Slideshow'].removeAction(MENU['Slideshow'].children()[0])
        
    def move(self, delta=0):
        
        if self.slideshow.isActive() and self.stack.currentIndex == 1:
            
            print('Video: ', self.stack.currentIndex == 1)
            print('Slideshow: ', self.slideshow.isActive())
            print('EndofMedia: ', self.video.mediaStatus == QMediaPlayer.EndOfMedia)
            # return 0
            
        if not self.model.gallery:
            self.image.no_image()
            return 0
        
        self.index = (self.index + delta) % len(self.model.gallery)
        path = self.model.index(self.index).data(Qt.UserRole)[0]
        self.setWindowTitle(f'{Path(path).name} - Slideshow')

        if path is None: pixmap = QPixmap()
        else:
            if path.endswith(('.jpg', '.png', 'webp')):
                image = QImage(path)
                path = None
            elif path.endswith(('.gif', '.mp4', '.webm')):
                image = get_frame(path)
            
            pixmap = QPixmap(image).scaled(
                self.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )

        self.image.update(pixmap)
        self.stack.setCurrentIndex(0)
        self.video.update(path)
        
        if self.slideshow.isActive(): self.slideshow.start()
    
    def fullscreen(self):

        if self.isFullScreen():

            self.timer.stop()
            self.image.setStyleSheet('background: ')
            self.fullAction.setText('Fullscreen')
            self.setCursor(Qt.ArrowCursor)
            self.showMaximized()
            self.menubar.show()

        else:

            self.image.setStyleSheet('background: black')
            self.fullAction.setText('Exit fullscreen')
            self.setCursor(Qt.BlankCursor)
            self.menubar.hide()
            self.showFullScreen()

    def rotate(self, sign):

        path = self.model.index(self.index).data(Qt.UserRole)[0]

        if path.endswith(('jpg', 'png', 'webp')):
            self.image.rotate(path, sign)
        
        else:
            self.video.rotate(path, sign)
            
        self.move()

    def copy(self):
        
        path = self.model.index(self.index).data(Qt.UserRole)[0]

        if path.endswith(('gif', '.mp4', '.webm')):
            return

            path = mktemp(suffix='.png')
            image = ImageGrab.grab(
                (0, 0, self.width(),self.height())
                )
            image.save(path)

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(path, mode=cb.Clipboard)

    def delete(self):
        
        if self.stack.currentIndex():
            self.video.update(None)
        else: self.image.update(None)
        
        index = [self.model.index(self.index)]

        if self.parent:
            if self.parent.delete_records(index):
                del self.model.gallery[self.index]
                self.model.layoutChanged.emit()
                self.move()
        else:
            message = QMessageBox.question(
                None, 'Delete', 
                'Are you sure you want to delete this?',
                QMessageBox.Yes | QMessageBox.No
                )
            
            if message == QMessageBox.Yes:
                
                (ROOT / index[0]).unlink(True)
                del self.model.gallery[self.index]
                self.model.layoutChanged.emit()
                self.move()

    def openEditor(self):

        index = self.model.index(self.index)
        
        Properties(self.parent, [index.data(Qt.EditRole)])
    
    def playEvent(self, event=None):
        
        if event.text() == 'Pause': 

            self.slideshow.stop()
            return
        
        match MENU['Slideshow'].children()[6].checkedAction().text():
            
            case 'Speed - Slow': self.slideshow.start(30000)
                
            case 'Speed - Medium': self.slideshow.start(15000)
                
            case 'Speed - Fast': self.slideshow.start(5000)
          
    def contextMenuEvent(self, event):
        
        self.menu.popup(event.globalPos())

    def menuPressEvent(self, event=None):

        action = event.text()
        
        if action == 'Exit': self.close()
        
    def keyPressEvent(self, event):

        key_press = event.key()
        video = self.stack.currentIndex()
        alt = event.modifiers() == Qt.AltModifier
        ctrl = event.modifiers() == Qt.ControlModifier
        shift = event.modifiers() == Qt.ShiftModifier

        if key_press in (Qt.Key_Right, Qt.Key_Left):
            
            self.move(1 if key_press == Qt.Key_Right else -1)
            
        elif video and key_press in (Qt.Key_Home, Qt.Key_End):
            
            if key_press == Qt.Key_Home: self.video.position(0)
            else: self.video.position(0)
            
        elif video and key_press in (Qt.Key_Period, Qt.Key_Comma):

            sign = 1 if key_press == Qt.Key_Period else -1
            if ctrl: self.video.position(sign * 50)
            else: self.video.position(sign * 5000)
        
        elif video and key_press in (Qt.Key_Up, Qt.Key_Down):

            sign = 1 if key_press == Qt.Key_Up else -1
            if ctrl: self.video.volume(sign * 1)
            else: self.video.volume(sign * 10)
        
        elif video and key_press == Qt.Key_Space: self.video.pause()
        
        elif video and key_press == Qt.Key_M: self.video.mute()
        
        elif key_press == Qt.Key_Delete: self.delete()
        
        elif key_press == Qt.Key_F11: self.fullscreen()

        elif key_press == Qt.Key_Escape:
            
            if self.isFullScreen(): self.fullscreen()
            else: self.close()
        
        elif alt:
            
            if key_press in (Qt.Key_Return, Qt.Key_Enter): self.openEditor()
            
        elif ctrl:
            
            if shift and key_press == Qt.Key_C: opy_to(self, [self.model.index(self.index)])
            
            elif key_press == Qt.Key_C: self.copy()
            
            elif key_press == Qt.Key_W: self.close()
    
    def mousePressEvent(self, event):
        
        if event.button() == Qt.MouseButton.LeftButton:
            
            if event.x() > (self.width() * .5): self.move(+1)
            elif event.x() < (self.width() * .5): self.move(-1)
    
    def mouseMoveEvent(self, event):
        
        if self.isFullScreen():

            self.setCursor(Qt.ArrowCursor)
            self.timer.start(1500)
        
    def closeEvent(self, event): 
        
        self.slideshow.stop()
        self.video.update(None)

class Model(QStringListModel):

    def __init__(self, parent, gallery):

        QStringListModel.__init__(self, parent)
        self.gallery = gallery
    
    def rowCount(self, parent=None): return len(self.gallery)

    def data(self, index, role):

        index = index.row()

        if role == Qt.EditRole:
            
            data = self.gallery[index]
            
            path = {data[0]}
            artist = set(data[1].split())
            tags = set(data[2].split())
            rating = {data[3]}
            stars = {data[4]}
            type = {data[5]}
            site = {data[6]}

            tags.discard('qwd')
            
            return path, tags, artist, stars, rating, type, site
        
        if role == Qt.UserRole: return self.gallery[index]
        
        if role == 300: return index
        
        return QVariant()
