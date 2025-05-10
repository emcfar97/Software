import ffmpeg

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QScrollArea, QLabel

class Filmstrip(QScrollArea):
     
    def __init__(self, parent):
         
        super(Filmstrip, self).__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        self.mod = 1000
        self.scale = 400
        self.tile = 10
        self.output = r'GUI\videosplitter\filmstrip.png'
    
    def create_widgets(self):
        
        self.pixmap = QPixmap()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
    
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        
    def set_filmstrip(self, file):
        
        select = f'not(mod(n\,{self.mod}))'
        scale = f'{self.scale}:-2'
        tile = f'{self.tile}x1'

        ffmpeg.input(file) \
            .output(self.output, 
                update=1, vframes=1, loglevel='error',
                vf=f'select={select}, scale={scale}, tile={tile}'
                ) \
            # .run(overwrite_output=True)
            
        self.pixmap.load(self.output)
        self.label.setPixmap(self.pixmap.scaledToHeight(
            self.height() - int(self.height() * .095)
            ))
        
    def resizeEvent(self, event):
        
        if not self.pixmap.isNull():
            
            self.label.setPixmap(self.pixmap.scaledToHeight(
                self.height() - int(self.height() * .095)
                ))