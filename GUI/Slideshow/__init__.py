'''
App for displaying images and video. Currently only works with Manage Database.
'''
from pathlib import Path
from tempfile import mktemp
from PyQt6.QtGui import QAction, QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer, QStringListModel, QVariant
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMenu

from GUI.utils import get_frame, copy_to
from GUI.propertiesView import Properties
from GUI.slideshow.imageViewer import imageViewer
from GUI.slideshow.videoPlayer import videoPlayer

from dotenv import load_dotenv

class Slideshow(QMainWindow):

    def __init__(self, parent, gallery=list(), index=0):

        super(Slideshow, self).__init__()
        self.parent = parent
        self.configure_gui(index)
        self.create_widgets(gallery)
        self.create_menu()
        self.showMaximized()
        self.activateWindow()

    def configure_gui(self, index):
        
        self.index = index
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

    def create_widgets(self, gallery):
        
        self.model = Model(self, gallery)

        self.image = imageViewer(self)
        self.video = videoPlayer(self)
        self.stack.addWidget(self.image)
        self.stack.addWidget(self.video)
        
        self.setMouseTracking(True)
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.BlankCursor)
            )
        self.move()

    def create_menu(self):

        self.menubar = self.menuBar()
        self.menubar.triggered.connect(self.menuPressEvent)
        
        # File
        file = self.menubar.addMenu('File')
        file.addAction('Copy Image to')
        file.addSeparator()
        file.addAction('Exit', self.close, shortcut='Ctrl+W')
        
        # View
        view = self.menubar.addMenu('View')
        view.addAction('Fullscreen', self.fullscreen, shortcut='F11')
        
        # Help
        help = self.menubar.addMenu('Help')
        
        menu = QMenu(self)

        self.full = QAction(
            'Fullscreen', menu, triggered=self.fullscreen
            )
        menu.addAction(self.full)
        
        menu.addSeparator()
        menu.addAction(QAction(
            'Rotate right', menu, triggered=lambda: self.rotate(+1)
            ))
        menu.addAction(QAction(
            'Rotate left', menu, triggered=lambda: self.rotate(-1)
            ))
        
        menu.addSeparator()
        menu.addAction(QAction(
            'Copy', menu, triggered=self.copy
            ))
        menu.addAction(QAction(
            'Delete', menu, triggered=self.delete
            ))
        
        menu.addSeparator()
        menu.addAction(QAction(
            'Properties', menu, triggered=self.openEditor
            ))

        self.menu = menu

    def move(self, delta=0):
        
        if not self.model.gallery:
            self.image.no_image()
            return 0
        
        self.index = (self.index + delta) % len(self.model.gallery)
        path = self.model.index(self.index).data(Qt.ItemDataRole.UserRole)[0]
        self.setWindowTitle(f'{Path(path).name} - Slideshow')

        if path is None: pixmap = QPixmap()
        else:
            if path.endswith(('.jpg', '.png')):
                image = path; path = None
            else: image = get_frame(path)
            
            pixmap = QPixmap(image).scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                )

        self.image.update(pixmap)
        self.stack.setCurrentIndex(0)
        self.video.update(path)
    
    def fullscreen(self):

        if self.isFullScreen():

            self.timer.stop()
            self.image.setStyleSheet('background: ')
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.full.setText('Fullscreen')
            self.menubar.show()
            self.showNormal()

        else:

            self.image.setStyleSheet('background: black')
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.full.setText('Exit fullscreen')
            self.menubar.hide()
            self.showFullScreen()

    def rotate(self, sign):

        path = self.model.index(self.index).data(Qt.UserRole)[0]

        if path.endswith(('jpg', 'png')):self.image.rotate(path, sign)
        
        else: self.video.rotate(path, sign)
            
        self.move()
        
    def copy(self):
        
        index = self.model.index(self.index)
        path = index.data(Qt.ItemDataRole.UserRole)[0]

        if path.endswith(('gif', '.mp4', '.webm')):
            
            path = mktemp(suffix='.png')
            frame = self.video.capture()

        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)
        clipboard.setText(path, mode=clipboard.Clipboard)
        
    def delete(self):
        
        if self.stack.currentIndex(): self.video.update(None)
        else: self.image.update(None)
        
        index = [self.model.index(self.index)]

        if self.parent.delete_records(index):
            
            del self.model.gallery[self.index]
            self.model.layoutChanged.emit()

        self.move()
        
    def openEditor(self):

        index = self.model.index(self.index)
        
        Properties(self.parent, [index.data(Qt.ItemDataRole.EditRole)])
        
    def playEvent(self, event):
        
        match self.play_menu.activeAction().text:
            
            case 'Speed - Slow': pass
            case 'Speed - Medium': pass
            case 'Speed - Fast': pass
          
    def contextMenuEvent(self, event): self.menu.popup(event.globalPos())

    def menuPressEvent(self, event=None):

        match event.text():
            
            case 'Copy Image to':
                
                copy_to(self, [self.model.index(self.index)])

            case 'Exit': self.close()

    def keyPressEvent(self, event):

        key_press = event.key()
        video = self.stack.currentIndex()
        alt = event.modifiers() == Qt.KeyboardModifier.AltModifier
        ctrl = event.modifiers() == Qt.KeyboardModifier.ControlModifier
        
        if alt:
            
            if key_press in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.openEditor()
            
            if key_press == Qt.Key.Key_F4: self.close()
            
        elif ctrl:
            
            if key_press == Qt.Key.Key_C: self.copy()
            
        elif video:
            
            match event.key():
                
                case (Qt.Key.Key_Home, Qt.Key.Key_End):
                    
                    if key_press == Qt.Key.Key_Home: self.video.position(0)
                    else: self.video.position(0)
                    
                case (Qt.Key.Key_Period, Qt.Key.Key_Comma):

                    sign = 1 if key_press == Qt.Key.Key_Period else -1
                    if ctrl: self.video.position(sign * 50)
                    else: self.video.position(sign * 5000)
                
                case (Qt.Key.Key_Up, Qt.Key.Key_Down):

                    sign = 1 if key_press == Qt.Key.Key_Up else -1
                    if ctrl: self.video.volume(sign * 1)
                    else: self.video.volume(sign * 10)
                
                case Qt.Key.Key_Space: self.video.pause()
                
                case Qt.Key.Key_M: self.video.mute()

        else:
            
            match event.key():
            
                case (Qt.Key.Key_Right|Qt.Key.Key_Left):
                    
                    self.move(1 if key_press == Qt.Key.Key_Right else -1)
                
                case Qt.Key.Key_Delete: self.delete()
                
                case Qt.Key.Key_F11: self.fullscreen()

                case Qt.Key.Key_Escape:
                    
                    if self.isFullScreen(): self.fullscreen()
                    else: self.close()

    def mouseMoveEvent(self, event):
        
        if self.isFullScreen():

            self.setCursor(Qt.ArrowCursor)
            self.timer.start(1500)
        
    def mousePressEvent(self, event):
        
        if event.button() == Qt.MouseButton.LeftButton:
            
            if event.x() > (self.width() * .5): self.move(+1)
            elif event.x() < (self.width() * .5): self.move(-1)
    
    def closeEvent(self, event): self.video.update(None)

class Model(QStringListModel):

    def __init__(self, parent, gallery):

        QStringListModel.__init__(self, parent)
        self.gallery = gallery
    
    def rowCount(self, parent=None): return len(self.gallery)

    def data(self, index, role):

        index = index.row()

        match role:
            
            case Qt.ItemDataRole.EditRole:
                
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
            
            case Qt.ItemDataRole.UserRole: return self.gallery[index]
            
            case 300: return index
            
        return QVariant()