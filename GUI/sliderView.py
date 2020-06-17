import qimage2ndarray
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from . import *

class Slideshow(QMainWindow):
    
    def __init__(self, parent, gallery, index):
        
        super().__init__()
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
        self.gallery = gallery
        self.index = index
        self.move(0)
        self.showFullScreen()
    
    def configure_gui(self):
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        resolution = self.parent.size()

        self.setGeometry(
            0, 0, resolution.width(),  resolution.height() + 20
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
            self.label.setPixmap(pixmap)
            self.video.player.stop()
        
        elif path.endswith(('gif', '.webm', '.mp4')):
            
            image = VideoCapture(path).read()[-1]
            image = qimage2ndarray.array2qimage(image).rgbSwapped()
            pixmap = QPixmap(image).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            self.label.setPixmap(pixmap)
            self.video.update(path)
        
    def keyPressEvent(self, sender):

        key_press = sender.key()
            
        if key_press == Qt.Key_Right: self.move(+1)
        elif key_press == Qt.Key_Left: self.move(-1)        
        elif key_press == Qt.Key_Escape: 
            
            self.stack.setCurrentIndex(0)
            self.hide()
            
    def mouseMoveEvent(self, sender):
        
        self.timer.stop()
        self.setCursor(Qt.ArrowCursor)
        self.timer.start(1500)
    
class videoPlayer(QVideoWidget):

    def __init__(self, parent):
        
        super().__init__(parent)
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.player.setVolume(50) 

    def update(self, path):

        self.player.setMedia(
            QMediaContent(QUrl.fromLocalFile(path))
            )
        self.player.play()
        self.setFocus()

    def mediaStatusChanged(self, status):
        
        if status == QMediaPlayer.EndOfMedia: 
            self.player.play()

        elif status != QMediaPlayer.LoadingMedia:
            self.parent().setCurrentIndex(1) 

    def keyPressEvent(self, sender):
        
        key_press = sender.key()
        ctrl = sender.modifiers() == Qt.ControlModifier

        if key_press == Qt.Key_Space:
            
            status = self.player.state()
            if status == QMediaPlayer.PlayingState: self.player.pause()
            elif status == QMediaPlayer.PausedState: self.player.play()
            
        elif key_press == Qt.Key_Home: self.player.setPosition(0)
            
        elif key_press == Qt.Key_End: self.player.setPosition(0)  
            
        elif key_press == Qt.Key_Period:

            if ctrl:
                self.player.setPosition(self.player.position() + 50)
            else:
                self.player.setPosition(self.player.position() + 5000)
            
        elif key_press == Qt.Key_Comma:
            
            if ctrl:
                self.player.setPosition(self.player.position() - 50)
            else:
                self.player.setPosition(self.player.position() - 5000)
        
        elif key_press == Qt.Key_Up:
            
            if ctrl:
                self.player.setPosition(self.player.volume() + 1)
            else:
                self.player.setVolume(self.player.volume() + 10)
            
        elif key_press == Qt.Key_Down:
            
            if ctrl:
                self.player.setPosition(self.player.volume() - 1)
            else:
                self.player.setVolume(self.player.volume() - 10)
    
        elif key_press == Qt.Key_Right:
            
            self.parent().parent().move(+1)
            self.parent().setCurrentIndex(0)
        
        elif key_press == Qt.Key_Left:
            
            self.parent().parent().move(-1)
            self.parent().setCurrentIndex(0)
        
        elif key_press == Qt.Key_Escape:
            
            self.player.stop()
            self.parent().keyPressEvent(sender)
    
    def wheelEvent(self, sender):
        
        if self.player.isAudioAvailable():
            
            delta = sender.angleDelta().y() // 12
            self.player.setVolume(self.player.volume() + delta)           
