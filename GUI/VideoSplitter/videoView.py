from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QSignalBlocker

from GUI.slideshow.videoPlayer import videoPlayer

class Video(QWidget):
     
    def __init__(self, parent):
         
        super(Video, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        # self.setStyleSheet('')
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def create_widgets(self):
        
        self.player = videoPlayer(self)
        self.controls = Controls(self)
        
        self.player.player.positionChanged.connect(self.controls.update_track)
        self.controls.track.sliderMoved.connect(self.update_position)
        # self.controls.track.valueChanged.connect(self.update_position)
        
        self.layout.addWidget(self.player, 7)
        self.layout.addWidget(self.controls, 1)

    def update(self, path):
        
        self.controls.track.setDisabled(True)
        self.player.update(path)
        self.player.pause()
        self.controls.track.setEnabled(True)

    def update_position(self, delta):
        
        with QSignalBlocker(self.player.player):
            
            duration = self.player.get_duration()
            position = int(duration * (delta / 100))
            
            self.player.set_position(position, 2)
        
        print(self.player.player.position())
        
        duration = self.parent().player.get_duration()
        
        if duration != 0: 
            
            position = int((delta / duration) * 100)
            self.track.setSliderPosition(position)