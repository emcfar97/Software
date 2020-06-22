import qimage2ndarray
from . import *

class Preview(QWidget):
    
    def __init__(self, parent, type_):
        
        super().__init__(parent)
        self.type = type_
        self.configure_gui()
        self.create_widgets()
    
    def configure_gui(self):
            
        size = self.parent().size() 
        
        if self.type == 'Manage Data':
            self.setGeometry(
                int(size.width() // 2), 0, 
                int(size.width() // 2), size.height() - 15
                )
            self.setStyleSheet('background: white')
            
        elif self.type == 'Gesture Draw':
            self.setGeometry(
                0, 0, 
                size.width(), size.height() - 20
                ) 
            self.setStyleSheet('background: black')
    
    def create_widgets(self):
        
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self.label.setAlignment(Qt.AlignCenter)
        self.timer = Countdown(self)
        
    def start(self, gallery, time):
    
        self.index = 0
        self.gallery = gallery
        self.time = time
        self.move(0)
        
        self.timer.time = self.time
        self.timer.setGeometry(
            self.width() * .8, self.height() * .8, 
            75, 75
            )        
        min, sec = divmod(time, 60)
        self.timer.setText(f'{min}:{sec:02d}')
        self.timer.timer.start(1000)                
                
    def move(self, delta):
        
        self.index = (self.index + delta) % len(self.gallery)
        self.show_image(self.gallery[self.index])
    
    def show_image(self, path):
                    
        try:
            width, height = self.width(), self.height()
                
            if path.endswith(('.mp4', '.webm')):
                
                image = VideoCapture(path).read()[-1]
                path = qimage2ndarray.array2qimage(image).rgbSwapped()
            
            pixmap = QPixmap(path).scaled(
                width, height, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            # ratio = pixmap.width() / pixmap.height()
            # self. = not (.5 <= ratio <= 2)

        except (ValueError, AttributeError): pixmap = QPixmap()
                
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
        self.setStyleSheet('background: white; font: 20px')

    def countdown(self):
        
        while self.time:
            
            self.time -= 1
            min, sec = divmod(self.time, 60)
            self.setText(f'{min}:{sec:02d}')
            self.setStyleSheet(
                f'''background: white; 
                color: {"red" if self.time <= 5 else "black"}; 
                font: 20px'''
                )   
        
        else: 
            parent = self.parent()
            CURSOR.execute(UPDATE, (parent.gallery[parent.index],))
            DATAB.commit()
            
            if parent.index + 1 < len(parent.gallery):
                
                parent.move(+1)
                self.time = parent.time
                min, sec = divmod(self.time, 60)
                self.setText(f'{min}:{sec:02d}')
                self.setStyleSheet(
                    f'''background: white; 
                    color: {"red" if self.time <= 5 else "black"}; 
                    font: 20px'''
                    )  
                self.timer.start(1000)  
                
            else:
                self.timer.stop()
                parent.label.setPixmap(QPixmap())
                self.setText('End of session')
                self.setStyleSheet(
                    'background: black; color: white; font: 17px'
                    )
                self.setGeometry(
                    int(parent.width() * .4), int(parent.height() * .1),
                    125, 75
                    )