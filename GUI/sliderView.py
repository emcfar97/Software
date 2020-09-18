import qimage2ndarray
from cv2 import VideoCapture
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QSlider, QPushButton, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QFormLayout, QLabel, QLineEdit 
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

class Slideshow(QMainWindow):
    
    def __init__(self, parent):
        
        super().__init__()
        self.parent = parent
        self.configure_gui()
        self.create_widgets()
    
    def configure_gui(self):
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.setGeometry(
            0, 0, self.parent.width(),  self.parent.height()
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
        except (FileNotFoundError, ValueError):
            del self.gallery[self.index]
            self.show_image(self.gallery[self.index][0])
    
    def show_image(self, path):
        
        if path.lower().endswith(('.jpg', '.png')):
            
            pixmap = QPixmap(path).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            path = None
        
        elif path.lower().endswith(('.gif', '.webm', '.mp4')):
            
            image = VideoCapture(path).read()[-1]
            image = qimage2ndarray.array2qimage(image).rgbSwapped()
            pixmap = QPixmap(image).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio
                )
                
        self.label.setPixmap(pixmap)
        self.stack.setCurrentIndex(0)
        self.video.update(path)
        
    def keyPressEvent(self, sender):

        key_press = sender.key()
        video = self.stack.currentIndex()
        ctrl = sender.modifiers() == Qt.ControlModifier
            
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
        
        elif key_press == Qt.Key_Escape:
            
            if video: self.video.update(None)
            self.hide()
            
    def mouseMoveEvent(self, sender):
        
        self.timer.stop()
        self.setCursor(Qt.ArrowCursor)
        self.timer.start(1500)
    
    def wheelEvent(self, sender):
        
        self.video.volume(sender.angleDelta().y() // 12)  
    
    def closeEvent(self, sender): self.video.update(None)

class videoPlayer(QVideoWidget):

    def __init__(self, parent):
        
        super().__init__(parent)
        self.player = QMediaPlayer()
        self.player.setVolume(50) 
        self.player.setVideoOutput(self)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        # self.player.stateChanged.connect(self.mediaStateChanged)
        # self.player.positionChanged.connect(self.positionChanged)
        # self.player.durationChanged.connect(self.durationChanged)

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

        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        #     self.playButton.setIcon(
        #             self.style().standardIcon(QStyle.SP_MediaPause))
        # else:
        #     self.playButton.setIcon(
        #             self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):

        self.parent().controls.timeline.setValue(position)

    def durationChanged(self, duration):

        self.parent().controls.total = duration

class Controls(QWidget):
    
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):

        self.layout = QVBoxLayout()
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.valueChanged.connect(self.playback)
        self.options = QHBoxLayout()
        
        self.setLayout(self.layout)
        self.layout.addWidget(self.timeline)
        self.layout.addLayout(self.options)
        
    def create_widgets(self):
        
        self.play = self.create_button('SP_MediaPlay', self.playback, 1)
        self.pause = self.create_button('SP_MediaPause', self.playback, 2)
        self.stop = self.create_button('SP_MediaStop', self.playback, 3)

        self.seek_b = self.create_button('SP_MediaSkipBackward', self.seek, 0)
        self.skip_b = self.create_button('SP_MediaSeekBackward', self.skip, 0)
        self.seek_f = self.create_button('SP_MediaSeekForward', self.seek, 1)
        self.skip_f = self.create_button('SP_MediaSkipForward', self.skip, 1)

        self.time = QLabel('00:00:000 / 00:00:000')
        self.options.addWidget(self.time)
        self.sound = self.create_button('SP_MediaVolume', self.mute)
        self.volume = QSlider(Qt.Horizontal)
        self.volume.valueChanged.connect(self.volumeChanged)
        self.options.addWidget(self.volume)
        
    def create_button(self, icon, slot, lamb=None):

        button = QPushButton(self)
        if lamb: button.clicked.connect(lambda: slot(lam))
        else: button.clicked.connect(slot)
        button.setIcon(
            self.style().standardIcon(getattr(QStyle, icon))
            )
        self.options.addWidget(button)

        return button

    def playback(self, sender):
        
        slider = self.timeline.value()
        current = self.total * (slider / 100)
        self.time.setText(
            '{:02.0f}:{:02.0f}:{:03.0f} / {:02.0f}:{:02.0f}:{:03.0f}'
            .format(*divmod(current, 60), 0, *divmod(self.total, 60), 0)
            )

    def playback(self, sender):

        if sender == 1: self.video.play()
        elif sender == 2: self.video.pause()
        elif sender == 3: self.video.stop()
    
    def seek(self, sender):

        print(sender)
    
    def skip(self, sender):

        if sender: self.parent().move(1)
        else: self.parent().move(-1)
    
    def mute(self, op=['SP_MediaVolumeMuted', 'SP_MediaVolume']):
        
        muted = op[self.video.player.isMuted()]
        self.sound.setIcon(QIcon(muted))

    def volumeChanged(self, sender):

        self.parent().video.volume(self.volume.value())
