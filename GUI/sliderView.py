import qimage2ndarray
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from . import *

class Slideshow(QMainWindow):
    
    def __init__(self, parent, resolution):
        
        super().__init__()
        self.parent = parent
        self.configure_gui(resolution)
        self.create_widgets()
    
    def configure_gui(self, resolution):
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.setGeometry(
            0, 0, resolution.width(),  resolution.height()
            )
        self.setStyleSheet('background: black')
          
    def create_widgets(self):
        
        self.label = QLabel(self)
        self.video = videoPlayer(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.label)
        self.stack.addWidget(self.video)
        
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.video.setMouseTracking(True)
        
        self.timer = QTimer()
        self.setCursor(Qt.BlankCursor)
        self.timer.timeout.connect(
            lambda: self.setCursor(Qt.BlankCursor)
            )               

    def update(self, gallery, index):

        self.gallery = gallery
        self.index = index
        self.move(0)
        self.showFullScreen()

    def move(self, delta):
        
        self.index = (self.index + delta) % len(self.gallery)
        try: self.show_image(self.gallery[self.index][0])
        except FileNotFoundError:
            del self.gallery[self.index]
            self.show_image(self.gallery[self.index][0])
    
    def show_image(self, path):
        
        if path.endswith(('.jpg', '.jpeg', '.png')):
            
            pixmap = QPixmap(path).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            path = None
        
        elif path.endswith(('.gif', '.webm', '.mp4')):
            
            image = VideoCapture(path).read()[-1]
            image = qimage2ndarray.array2qimage(image).rgbSwapped()
            pixmap = QPixmap(image).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio, 
                )
                
        self.label.setPixmap(pixmap)
        self.video.update(path)
        
    def keyPressEvent(self, sender):

        key_press = sender.key()
        video = self.stack.currentIndex()
        ctrl = sender.modifiers() == Qt.ControlModifier
            
        if key_press in (Qt.Key_Right, Qt.Key_Left):
            
            sign = 1 if key_press == Qt.Key_Right else -1
            self.move(sign * 1)
            if video: self.stack.setCurrentIndex(0)
            
        elif video and key_press in (Qt.Key_Home, Qt.Key_End):
            
            if key_press == Qt.Key_Home: self.player.setPosition(0)
            else: self.player.setPosition(0)
            
        elif video and key_press in (Qt.Key_Period, Qt.Key_Comma):

            sign = 1 if key_press == Qt.Key_Period else -1
            if ctrl: self.video.position(sign * 50)
            else: self.video.position(sign * 5000)
        
        elif video and key_press in (Qt.Key_Up, Qt.Key_Down):

            sign = 1 if key_press == Qt.Key_Up else -1
            if ctrl: self.video.position(sign * 1)
            else: self.video.position(sign * 10)
        
        elif video and key_press == Qt.Key_Space: self.video.pause()

        elif key_press == Qt.Key_Escape:
            
            if video: self.video.stop()
            self.hide()
            
    def mouseMoveEvent(self, sender):
        
        self.timer.stop()
        self.setCursor(Qt.ArrowCursor)
        self.timer.start(1500)
    
    def wheelEvent(self, sender):
        
        self.video.volume(sender.angleDelta().y() // 12)  
    
class videoPlayer(QVideoWidget):

    def __init__(self, parent):
        
        super().__init__(parent)
        self.player = QMediaPlayer()
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

    def stop(self): self.player.stop()

    def mediaStatusChanged(self, status):
        
        if status == QMediaPlayer.EndOfMedia: self.player.play()

        elif status not in (2, 1):

            self.parent().setCurrentIndex(1)      