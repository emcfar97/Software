from moviepy.editor import VideoFileClip
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtMultimedia import QMediaPlayer, QVideoSink, QAudioOutput

class videoPlayer(QMainWindow):

    playing = pyqtSignal()
    
    def __init__(self, parent):
        
        super(videoPlayer, self).__init__(parent)
        self.player = QMediaPlayer(self)
        self.videoOutput = QVideoWidget(self)
        self.videoSink = QVideoSink(self)
        self.audioOutput = QAudioOutput(self)
        
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.setVideoOutput(self.videoOutput)
        self.player.setAudioOutput(self.audioOutput)
        
        self.audioOutput.setVolume(.5)
        
        self.player.mediaStatusChanged.connect(self.mediaStatusChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.audioOutput.volumeChanged.connect(self.positionChanged)
        
        self.setCentralWidget(self.videoOutput)
        
    def update(self, path):
        
        if path: 
            
            path = QUrl.fromLocalFile(path)
            self.player.setSource(path)
            self.play()
            
        else: self.stop()

    def capture(self): pass
    
    def rotate(self, path, sign):
        
        self.update(None)
        clip = VideoFileClip(path)
        clip.rotate(90 * sign)
        clip.write_videofile(path)
        clip.close()

    def play(self): self.player.play()

    def pause(self):

        match self.player.playbackState():

            case QMediaPlayer.PlaybackState.PlayingState: self.player.pause()
            case QMediaPlayer.PlaybackState.PausedState: self.player.play()
            case QMediaPlayer.PlaybackState.StoppedState: self.player.play()

    def stop(self): self.player.stop()

    def set_position(self, delta):

        self.player.setPosition(self.player.position() + delta)

    def set_volume(self, delta):
        
        if self.player.hasAudio(): 

            self.audioOutput.setVolume(self.audioOutput.volume() + delta)

    def mute(self):
        
        if self.player.hasAudio():
    
            self.audioOutput.setMuted(not self.audioOutput.isMuted())

    def get_duration(self): return self.player.duration()
    
    def positionChanged(self, event): pass
    
    def volumeChanged(self, event): pass
        
    def mediaStatusChanged(self, status):
        
        match status:
            
            case QMediaPlayer.MediaStatus.BufferedMedia: self.playing.emit()
            
            case QMediaPlayer.MediaStatus.InvalidMedia:
                
                message = QMessageBox()
                message.setWindowTitle('Error')
                message.setText(f'Invalid Media: {self.source}')
                
            # case _: print(status)
            
    def wheelEvent(self, event): self.volume(event.angleDelta().y() // 12)  