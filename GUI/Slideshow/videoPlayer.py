from moviepy.editor import VideoFileClip
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

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
    
    def rotate(self, path, sign):
        
        self.update(None)
        clip = VideoFileClip(path)
        clip.rotate(90 * sign)

        if path.endswith(('gif')):
            clip.write_gif(path)
        else: 
            clip.write_videofile(path)

        clip.close()

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