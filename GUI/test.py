import qimage2ndarray
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QSlider, QPushButton, QButtonGroup, QSizePolicy
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
# from . import *

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
        
        if path.endswith(('.jpg', '.png')):
            
            pixmap = QPixmap(path).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            path = None
        
        elif path.endswith(('.gif', '.webm', '.mp4')):
            
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
        self.player.positionChanged.connect(self.positionChanged)
        self.player.durationChanged.connect(self.durationChanged)

    def update(self, path):
        
        if path: path = QUrl.fromLocalFile(path)
        self.player.setMedia(QMediaContent(path))
        self.player.play()
    
    def pause(self):

        status = self.player.state()
        if status == QMediaPlayer.PlayingState: self.player.pause()
        elif status == QMediaPlayer.PausedState: self.player.play()

    def stop(self): self.player.stop()

    def position(self, delta):

        self.player.setPosition(self.player.position() + delta)

    def volume(self, delta):
        
        if self.player.isAudioAvailable(): 
            
            self.player.setVolume(self.player.volume() + delta)

    def mute(self):
        
        if self.player.isAudioAvailable(): 
    
            self.player.setMuted(not self.player.isMuted())

    def mediaStatusChanged(self, status):
        
        if status == QMediaPlayer.EndOfMedia: self.player.play()

        elif status not in (2, 1): pass

            # self.parent().setCurrentIndex(1)      

        # if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        #     self.playButton.setIcon(
        #             self.style().standardIcon(QStyle.SP_MediaPause))
        # else:
        #     self.playButton.setIcon(
        #             self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        
        parent = self.parent()
        while parent.windowTitle() != 'Test': parent = parent.parent()
        if total := parent.controls.total != 0:
            position = position / total
            parent.controls.timeline.setValue(position)

    def durationChanged(self, duration):
        
        parent = self.parent()
        while parent.windowTitle() != 'Test': parent = parent.parent()
        parent.controls.total = duration

class Controls(QWidget):
    
    def __init__(self, parent):
         
        super().__init__(parent)
        self.total = 0
        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):

        self.layout = QVBoxLayout()
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.valueChanged.connect(self.duration)
        self.options = QHBoxLayout()
        
        self.setLayout(self.layout)
        self.layout.addWidget(self.timeline)
        self.layout.addLayout(self.options)
        self.setFixedHeight(75)
        # self.setMouseTracking(True)
        
    def create_widgets(self):
        
        self.play = self.create_button(QStyle.SP_MediaPlay, self.playback, 1)
        self.pause = self.create_button(QStyle.SP_MediaPause, self.playback, 2)
        self.stop = self.create_button(QStyle.SP_MediaStop, self.playback, 3)

        self.seek_b = self.create_button(QStyle.SP_MediaSkipBackward, self.seek, 0)
        self.skip_b = self.create_button(QStyle.SP_MediaSeekBackward, self.skip, 0)
        self.seek_f = self.create_button(QStyle.SP_MediaSeekForward, self.seek, 1)
        self.skip_f = self.create_button(QStyle.SP_MediaSkipForward, self.skip, 1)

        self.time = QLabel('00:00:000 / 00:00:000')
        self.options.addWidget(self.time)
        
        self.sound = self.create_button(QStyle.SP_MediaVolume, self.mute)
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setFixedWidth(50)
        self.volume.valueChanged.connect(self.volumeChanged)
        self.options.addWidget(self.volume)
        
    def create_button(self, icon, slot, lamb=None):

        button = QPushButton(self)
        if lamb: button.clicked.connect(lambda: slot(lamb))
        else: button.clicked.connect(slot)
        button.setIcon(self.style().standardIcon(icon))
        self.options.addWidget(button)
        
        policy = button.sizePolicy()
        policy.setHeightForWidth(True)
        button.setSizePolicy(policy)

        return button

    def duration(self, sender):
        
        # slider = self.timeline.value()
        current = self.total * (sender / 100)
        self.time.setText(
            '{:02.0f}:{:02.0f}:{:03.0f} / {:02.0f}:{:02.0f}:{:03.0f}'
            .format(*divmod(current, 60), 0, *divmod(self.total, 60), 0)
            )

    def playback(self, sender):

        if sender == 1: self.parent().video.play()
        elif sender == 2: self.parent().video.pause()
        elif sender == 3: self.parent().video.stop()
    
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

class Test(QMainWindow):
    
    def __init__(self, paths):
        
        super().__init__()
        self.setWindowTitle('Test')
        self.paths = paths        
        # resolution = Qapp.desktop().screenGeometry()
        # width, height = resolution.width(),  resolution.height()
        # self.setGeometry(0, 0, resolution.width(), resolution.height())
        
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.stack = QStackedLayout()
        self.stack.setStackingMode(QStackedLayout.StackAll)
        self.widget.setLayout(self.stack)
        # self.layout = QVBoxLayout()
        # self.widget.setLayout(self.layout)
        
        self.controls = Controls(self)
        self.controls.setParent(self)
        self.video = videoPlayer(self)
        self.video.setParent(self)
        
        self.video.update(self.paths[0])
        self.stack.addWidget(self.controls)
        self.stack.addWidget(self.video)
        
        self.showFullScreen()

if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel, QStyle
    from PyQt5.QtCore import Qt
    
    paths = [
        r"E:\Users\Emc11\Dropbox\ん\エラティカ 三\bd12888ec1548ef0af7e5d6f87ba9f22.gif", 
        r"E:\Users\Emc11\Dropbox\ん\エラティカ 三\284936fd8f83c61bdb04bc7a4ed3385f.gif", 
        r"E:\Users\Emc11\Dropbox\ん\エラティカ 三\a07cc1a653a47ac90dbd394c1ebefbaa.gif"
        ]

    Qapp = QApplication([])

    # app = Test(paths)
    
    h = Controls(None)
    h.show()
    
    def f(x): 
        print(playback.id(x))

    window = QWidget()
    
    playback = QButtonGroup(window)
    play_layout = QHBoxLayout(window)
    window.setLayout(play_layout)
    
    play = QPushButton(window)
    pause = QPushButton(window)
    stop = QPushButton(window)
    
    play.setIcon(window.style().standardIcon(QStyle.SP_MediaPlay))
    pause.setIcon(window.style().standardIcon(QStyle.SP_MediaPause))
    stop.setIcon(window.style().standardIcon(QStyle.SP_MediaStop))
    
    play_layout.addWidget(play)
    play_layout.addWidget(pause)
    play_layout.addWidget(stop)
    
    playback.addButton(play, 0)
    playback.addButton(pause, 1)
    playback.addButton(stop, 2)
    
    playback.buttonClicked.connect(f)
    
    window.show()

    Qapp.exec_()