from . import get_frame
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QLabel, QSizePolicy, QWidget

class Slideshow(QMainWindow):
    
    def __init__(self, parent):
        
        super(Slideshow, self).__init__()
        self.setWindowTitle('Slideshow')
        self.parent = parent
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        self.create_widgets()
          
    def create_widgets(self):
        
        self.label = QLabel(self)
        self.video = videoPlayer(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
            )
        self.stack.addWidget(self.label)
        self.stack.addWidget(self.video)
        
        self.timer = QTimer()
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.BlankCursor)
            )               

    def move(self, delta):
        
        self.index = (self.index + delta) % len(self.gallery)
        path = self.gallery[self.index][0]

        if path is None: pixmap = QPixmap()
        else:
            if path.endswith('.jpg'): 
                image = QImage(path)
                path = None
            elif path.endswith(('gif', '.mp4', '.webm')):
                image = get_frame(path)
            else: print(path)
            
            pixmap = QPixmap(image).scaled(
                self.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )

        self.label.setPixmap(pixmap)
        self.stack.setCurrentIndex(0)
        self.video.update(path)
        
    def keyPressEvent(self, event):

        key_press = event.key()
        video = self.stack.currentIndex()
        ctrl = event.modifiers() == Qt.ControlModifier
            
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
        
        elif key_press == Qt.Key_F11:

            fullscreen = self.isFullScreen()
            self.setMouseTracking(fullscreen)
            
            if fullscreen:
                self.video.setStyleSheet('background: ')
                self.setStyleSheet('background: ')   
                self.showMaximized()
            else:
                self.video.setStyleSheet('background: black')
                self.setStyleSheet('background: black')
                self.setCursor(Qt.BlankCursor)
                self.showFullScreen()

        elif key_press == Qt.Key_Escape:
            
            if self.isFullScreen():
                self.video.setStyleSheet('background: ')
                self.setStyleSheet('background: ') 
                self.showMaximized()
            else: 
                self.video.update(None)
                self.hide()

    def mouseMoveEvent(self, event):
        
        if self.isFullScreen():

            self.timer.stop()
            self.setCursor(Qt.ArrowCursor)
            self.timer.start(1500)
    
    def resizeEvent(self, event):

        if self.stack.currentIndex(): pass
        
        else:
            pixmap = self.label.pixmap().scaled(
                event.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            self.label.setPixmap(pixmap)

    def closeEvent(self, event): self.video.update(None)

class ImageViewer(QWidget):
    
    def __init__(self, parent):
        
        super(QWidget, self).__init__(parent)

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