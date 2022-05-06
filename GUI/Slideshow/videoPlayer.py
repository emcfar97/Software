from moviepy.editor import VideoFileClip
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QImageCapture, QAudioOutput

from GUI.slideshow.controls import Controls

class videoPlayer(QVideoWidget):

    def __init__(self, parent):
        
        super(videoPlayer, self).__init__(parent)
        self.capture = QImageCapture()
        self.player = QMediaPlayer(self)
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.player.setVideoOutput(self)
        
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.player.positionChanged.connect(self.positionChanged)
        
    def update(self, path):
        
        if not path: return
        
        path = QUrl.fromLocalFile(path)
        self.player.setSource(path)
        self.player.play()

    def capture(self): pass
    
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

        match self.player.PlaybackState:
            
            case QMediaPlayer.PlaybackState.PlayingState: self.player.pause()
            case QMediaPlayer.PlaybackState.PausedState: self.player.play()

    def stop(self): self.player.stop()

    def position(self, delta):

        self.player.setPosition(self.player.position() + delta)

    def volume(self, delta):
        
        if self.player.hasAudio(): 
            
            self.audioOutput.setVolume(self.player.volume() + delta)

    def mute(self):
        
        if self.player.hasAudio(): 
    
            self.player.setMuted(not self.player.isMuted())

    def positionChanged(self, event): pass
        
    def mediaStatusChanged(self, status):
        
        match status:
            
            case QMediaPlayer.MediaStatus.LoadedMedia:
                
                self.parent().setCurrentIndex(1)
                print(self.player.duration())
                
            case QMediaPlayer.MediaStatus.InvalidMedia:
                
                message = QMessageBox()
                message.setWindowTitle('Error')
                message.setText('The entered credentials are incorrect')
                
            case _: print(status)
            
    def wheelEvent(self, event): self.volume(event.angleDelta().y() // 12)  