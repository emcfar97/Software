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
        
    def start(self, gallery, time):
    
        self.index = 0
        self.gallery = gallery
        
        self.timer = Countdown(self, time)
        self.timer.setGeometry(
            self.width() * .8, self.height() * .8, 
            75, 75
            )
        self.move(0)
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

        except (ValueError, AttributeError): pixmap = QPixmap()
                
        self.label.setPixmap(pixmap)
        
    def keyPressEvent(self, sender):

        key_press = sender.key()
        if self.type == 'GestureDraw':
            
            if key_press == Qt.Key_Space: 
                
                timer = self.timer.timer
                if timer.isActive(): timer.stop()
                else: timer.start(1000)  
                
            elif key_press == Qt.Key_Escape: 

                parent = self.parent()
                self.timer.timer.close()
                parent.stack.setCurrentIndex(0)
                parent.gallery.ribbon.tags.clear()
                parent.gallery.ribbon.time.clear()
                parent.gallery.populate()
                        
class Countdown(QLabel):
    
    def __init__(self, parent, time):
        
        super().__init__(parent)
        self.time = [time, time]
        self.timer = QTimer()
        self.setAlignment(Qt.AlignCenter)
        self.timer.timeout.connect(self.countdown)
        self.setStyleSheet('background: white; font: 20px')

    def countdown(self):
        
        if self.time[1]:
            
            self.time[1] -= 1
            self.setText(f'{self.time[1] // 60}:{self.time[1] % 60:02d}')
            if self.time[1] <= 5: self.setStyleSheet(
                'background: white; color: red; font: 20px'
                )
            else: self.setStyleSheet(
                'background: white; color: black; font: 20px'
                )   
        
        else: 
            parent = self.parent()
            CURSOR.execute(UPDATE, (parent.gallery[parent.index],))
            DATAB.commit()
            
            if parent.index + 1 < len(parent.gallery):
                
                parent.move(+1)
                self.time[1] = self.time[0]
                self.timer.start(1000)  
                
            else:
                self.timer.stop()
                null = QPixmap(), QMovie()
                parent.label.setPixmap(null[0])
                parent.label.setMovie(null[1])
                
                self.setText('End of session')
                self.setStyleSheet(
                    'background: black; color: white; font: 17px'
                    )
                self.setGeometry(
                    int(parent.width() * .4), int(parent.height() * .1),
                    125, 75
                    )