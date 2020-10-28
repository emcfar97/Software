from . import GESTURE, CONNECTION, get_frame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QSizePolicy

class Preview(QLabel):
    
    def __init__(self, parent, color):
        
        super(Preview, self).__init__(parent)
        self.title = parent.windowTitle()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f'background: {color}')
        self.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
            )
        
    def show_image(self, path):
        
        if path is None: pixmap = QPixmap()
        
        else:
            if path.endswith(('.mp4', '.webm')):
                path = get_frame(path)
            
            pixmap = QPixmap(path).scaled(
                self.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )

        self.setPixmap(pixmap)
                     
class Timer(QLabel):
    
    def __init__(self, parent):
        
        super(QLabel, self).__init__(parent)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown)
        self.setAlignment(Qt.AlignCenter)

    def start(self, gallery,  time):
        
        parent = self.parent()
        self.gallery = gallery
        self.current = next(self.gallery)
        parent.show_image(self.current)
        
        self.setGeometry(
            parent.width() * .85, parent.height() * .85, 
            75, 75
            )
        self.setStyleSheet('background: white; font: 20px')
        
        self.time = [time, time]
        self.updateText()
        self.timer.start(1000)

    def updateText(self):

        self.setText('{}:{:02}'.format(*divmod(self.time[1], 60)))
        self.setStyleSheet(f'''
            background: white; font: 20px;
            color: {"red" if self.time[1] <= 5 else "black"}
            ''')   

    def pause(self):

        if self.timer.isActive(): self.timer.stop()
        else: self.timer.start(1000)
           
    def countdown(self):
        
        if self.time[1]:

            self.time[1] -= 1
            self.updateText()
        
        else:
            parent = self.parent()
            CONNECTION.execute(GESTURE, (self.current,), commit=1)
            
            try:
                self.current = next(self.gallery)
                parent.show_image(self.current)
                self.time[1] = self.time[0]
                self.updateText()

            except StopIteration:

                self.timer.stop()
                parent.show_image(None)
                self.setText('End of session')
                self.setStyleSheet(
                    'background: black; color: white; font: 17px'
                    )
                self.setGeometry(
                    parent.width() * .4, parent.height() * .1,
                    125, 75
                    )