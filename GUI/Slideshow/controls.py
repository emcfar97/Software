from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

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
        self.setFixedHeight(150)
        # self.setMouseTracking(True)
        
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
        self.volume.setFixedWidth(50)
        self.volume.valueChanged.connect(self.volumeChanged)
        self.options.addWidget(self.volume)
        
    def create_button(self, icon, slot, lamb=None):

        button = QPushButton(self)
        if lamb: button.clicked.connect(lambda: slot(lamb))
        else: button.clicked.connect(slot)
        button.setIcon(QIcon(icon))
        self.options.addWidget(button)

        return button

    def duration(self, event):
        
        # slider = self.timeline.value()
        current = self.total * (event / 100)
        self.time.setText(
            '{:02.0f}:{:02.0f}:{:03.0f} / {:02.0f}:{:02.0f}:{:03.0f}'
            .format(*divmod(current, 60), 0, *divmod(self.total, 60), 0)
            )

    def playback(self, event):

        if event == 1: self.parent().video.play()
        elif event == 2: self.parent().video.pause()
        elif event == 3: self.parent().video.stop()
    
    def seek(self, event):

        print(event)
    
    def skip(self, event):

        if event: self.parent().move(1)
        else: self.parent().move(-1)
    
    def mute(self, op=['SP_MediaVolumeMuted', 'SP_MediaVolume']):
        
        muted = op[self.video.player.isMuted()]
        self.sound.setIcon(QIcon(muted))

    def volumeChanged(self, event):

        self.parent().video.volume(self.volume.value())
