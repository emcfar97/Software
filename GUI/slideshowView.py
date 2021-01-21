from pathlib import Path
from . import get_frame
from .propertiesView import Properties
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtGui import QImage, QPixmap, QTransform
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMenu, QStackedWidget, QLabel, QAction

class Slideshow(QMainWindow):
    
    def __init__(self, parent):
        
        super(Slideshow, self).__init__()
        self.parent = parent
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.create_widgets()
          
    def create_widgets(self):
        
        self.image = imageViewer(self)
        self.video = videoPlayer(self)
        self.stack.addWidget(self.image)
        self.stack.addWidget(self.video)
        
        self.setMouseTracking(True)
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.BlankCursor)
            )
        
        # self.image.setParent(self)
        self.menu = self.create_menu()
    
    def create_menu(self):

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

        return menu

    def move(self, delta=0):
        
        self.index = (self.index + delta) % len(self.gallery)
        path = self.gallery[self.index][0]
        self.setWindowTitle(f'{Path(path).name} - Slideshow')

        if path is None: pixmap = QPixmap()
        else:
            if path.endswith(('.jpg', '.png')): 
                image = QImage(path)
                path = None
            elif path.endswith(('gif', '.mp4', '.webm')):
                image = get_frame(path)
            else: print(path)
            
            pixmap = QPixmap(image).scaled(
                self.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )

        self.image.update(pixmap)
        self.stack.setCurrentIndex(0)
        self.video.update(path)
    
    def fullscreen(self):

        if self.isFullScreen():
            self.timer.stop()
            self.image.setStyleSheet('background: ')
            self.full.setText('Fullscreen')
            self.setCursor(Qt.ArrowCursor)
            self.showNormal()

        else:
            self.image.setStyleSheet('background: black')
            self.full.setText('Exit fullscreen')
            self.setCursor(Qt.BlankCursor)
            self.showFullScreen()

    def rotate(self, sign):

        path = self.gallery[self.index][0]
        if path.endswith(('jpg', 'png')):
            QPixmap(path).transformed(
                QTransform().rotate(90 * sign), 
                Qt.SmoothTransformation
                ).save(path)
        else: pass
            # VideoFileClip(path).rotate(90 * sign)
        self.move()

    def copy(self):
        
        path = self.gallery[self.index][0]
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(path, mode=cb.Clipboard)

    def delete(self):
        
        path = self.gallery[self.index]
        self.move(1)
        if self.parent.delete_records(path, 0):
            del self.gallery[self.index]
        else: self.move(-1)

    def openEditor(self):
            
        data = self.gallery[self.index]
        
        path = {data[0]}
        artist = set(data[1].split())
        tags = set(data[2].split())
        rating = {data[3]}
        stars = {data[4]}
        type = {data[5]}
        site = {data[6]}

        tags.discard('qwd')

        index = path, tags, artist, stars, rating, type, site
        Properties(self.parent, [index])

    def contextMenuEvent(self, event):
        
        self.menu.popup(event.globalPos())

    def keyPressEvent(self, event):

        key_press = event.key()
        video = self.stack.currentIndex()
        alt = event.modifiers() == Qt.AltModifier
        ctrl = event.modifiers() == Qt.ControlModifier
        
        if alt:
            
            if key_press == Qt.Key_Return: self.openEditor()
            
        if ctrl:
            if key_press == Qt.Key_C: self.copy()

        elif key_press in (Qt.Key_Right, Qt.Key_Left):
            
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
            else: 
                self.video.update(None)
                self.hide()

    def mouseMoveEvent(self, event):
        
        if self.isFullScreen():

            self.setCursor(Qt.ArrowCursor)
            self.timer.start(1500)
        
    def closeEvent(self, event): self.video.update(None)

class imageViewer(QLabel):
    
    def __init__(self, parent):
        
        super(QWidget, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(
            self.parent().width() * .3, self.parent().height() * .3
            )
        # self.setScaledContents(True)
    
    def update(self, pixmap): self.setPixmap(pixmap)
    
    # def hasHeightForWidth(self):

    #     return self.pixmap() is not None

    # def heightForWidth(self, w):

    #     if self.pixmap():

    #         return int(w * (self.pixmap().height() / self.pixmap().width()))

    def resizeEvent(self, event):

        parent = self.parent().parent()
        if not parent.stack.currentIndex(): 
            
            image = QImage(parent.gallery[parent.index][0])
            
            pixmap = QPixmap(image).scaled(
                event.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
                
            self.setPixmap(pixmap)

class videoPlayer(QVideoWidget):

    def __init__(self, parent):
        
        super(QVideoWidget, self).__init__(parent)
        self.player = QMediaPlayer(self)
        self.player.setVolume(50) 
        self.player.setVideoOutput(self)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)

    def update(self, path):
        
        if path: path = QUrl.fromLocalFile(path)
        self.player.setMedia(QMediaContent(path))
        self.player.play()
    
    def pause(self):

        status = self.player.state()
        if status == QMediaPlayer.PlayingState: self.player.pause()
        elif status == QMediaPlayer.PausedState: self.player.play()

    def position(self, delta):

        self.player.setPosition(self.player.position() + delta)

    def volume(self, delta):
        
        if self.player.isAudioAvailable(): 
            
            self.player.setVolume(self.player.volume() + delta)

    def mute(self):
        
        if self.player.isAudioAvailable(): 
    
            self.player.setMuted(not self.player.isMuted())

    def stop(self): self.player.stop()

    def mediaStatusChanged(self, status):
        
        if status == QMediaPlayer.EndOfMedia: self.player.play()

        elif status not in (2, 1):

            self.parent().setCurrentIndex(1)
    
    def wheelEvent(self, event):
        
        self.volume(event.angleDelta().y() // 12)  