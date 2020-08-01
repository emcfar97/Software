import qimage2ndarray
from . import *

class Preview(QWidget):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
    
    def configure_gui(self):
            
        size = self.parent().size() 
        
        if self.parent().windowTitle() == 'Manage Data':
            self.setGeometry(
                int(size.width() // 2), 0, 
                int(size.width() // 2), size.height() - 15
                )
            self.setStyleSheet('background: white')
            
        elif self.parent().windowTitle() == 'Gesture Draw':
            self.setGeometry(
                0, 0, size.width(), size.height()
                ) 
            self.setStyleSheet('background: black')
    
    def create_widgets(self):
        
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setAlignment(Qt.AlignCenter)
        self.timer = Countdown(self)
        
    def start(self, gallery, time):
    
        self.gallery = gallery
        self.path = next(self.gallery)
        self.show_image(self.path)
        
        self.time = self.timer.time = time
        self.timer.setGeometry(
            self.width() * .8, self.height() * .8, 
            75, 75
            )
        self.timer.setStyleSheet('background: white; font: 20px')
        self.timer.setText('{}:{:02}'.format(*divmod(time, 60)))
        self.timer.timer.start(1000)                
                
    def show_image(self, path):

        if path: 
            if path.endswith(('.mp4', '.webm')):
                
                image = VideoCapture(path).read()[-1]
                path = qimage2ndarray.array2qimage(image).rgbSwapped()
            
            pixmap = QPixmap(path).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            # ratio = pixmap.width() / pixmap.height()
            # scrollbar = not (.5 <= ratio <= 2)

        else: pixmap = QPixmap()
                
        self.label.setPixmap(pixmap)
    
    def pause(self):

        if self.timer.timer.isActive(): 
            self.timer.timer.stop()
        else: self.timer.timer.start(1000)
                                
class Countdown(QLabel):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        self.timer = QTimer()
        self.setAlignment(Qt.AlignCenter)
        self.timer.timeout.connect(self.countdown)

    def countdown(self):
        
        if self.time:
            
            self.time -= 1
            self.setText('{}:{:02}'.format(*divmod(self.time, 60)))
            self.setStyleSheet(
                f'''background: white; 
                color: {"red" if self.time <= 5 else "black"}; 
                font: 20px'''
                )   
        
        else:
            parent = self.parent()
            CONNECTION.execute(UPDATE, (parent.path,), commit=1)
            
            try:
                parent.path = next(parent.gallery)
                parent.show_image(parent.path)
                self.time = parent.time
                self.setText('{}:{:02}'.format(*divmod(self.time, 60)))
                self.setStyleSheet(
                    f'''background: white; 
                    color: {"red" if self.time <= 5 else "black"}; 
                    font: 20px'''
                    )  

            except StopIteration:

                self.timer.stop()
                parent.show_image(None)
                self.setText('End of session')
                self.setStyleSheet(
                    'background: black; color: white; font: 17px'
                    )
                self.setGeometry(
                    int(parent.width() * .4), int(parent.height() * .1),
                    125, 75
                    )