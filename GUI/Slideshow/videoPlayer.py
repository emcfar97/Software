from moviepy.editor import VideoFileClip
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtMultimedia import QMediaPlayer, QImageCapture, QAudioOutput

from GUI.slideshow.controls import Controls

class videoPlayer(QMainWindow):

    def __init__(self, parent):
        
        super(videoPlayer, self).__init__(parent)
        self.player = QMediaPlayer(self)
        self.audioOutput = QAudioOutput(self)
        self.videoOutput = QVideoWidget(self)
        self.imageCapture = QImageCapture(self)
        self.player.setAudioOutput(self.audioOutput)
        self.player.setVideoOutput(self.videoOutput)
        self.setCentralWidget(self.videoOutput)
        
        self.audioOutput.setVolume(.5)
        
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        # self.player.positionChanged.connect(self.positionChanged)
        # self.audioOutput.volumeChanged.connect(self.positionChanged)
        
    def update(self, path):
        
        if path is None: return 
            
            
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

        match self.player.playbackState():

            case QMediaPlayer.PlaybackState.PlayingState: self.player.pause()
            case QMediaPlayer.PlaybackState.PausedState: self.player.play()

    def stop(self): 
        
        self.player.stop()

    def position(self, delta):

        self.player.setPosition(self.player.position() + delta)

    def volume(self, delta):
        
        if self.player.hasAudio(): 

            self.audioOutput.setVolume(self.audioOutput.volume() + delta)

    def mute(self):
        
        if self.player.hasAudio():
    
            self.audioOutput.setMuted(not self.audioOutput.isMuted())

    def positionChanged(self, event): pass
    
    def volumeChanged(self, event): pass
        
    def mediaStatusChanged(self, status):
        
        match status:
            
            case QMediaPlayer.MediaStatus.EndOfMedia: self.player.play()
        
            case QMediaPlayer.MediaStatus.LoadedMedia:
                
                self.parent().setCurrentIndex(1)
                
            case QMediaPlayer.MediaStatus.InvalidMedia:
                
                message = QMessageBox()
                message.setWindowTitle('Error')
                message.setText('Invalid Media')
                
            # case _: print(status)
            
    def wheelEvent(self, event): self.volume(event.angleDelta().y() // 12)  