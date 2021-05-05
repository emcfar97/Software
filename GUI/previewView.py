from . import GESTURE, MYSQL, get_frame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtWidgets import QLabel, QScrollArea

class Preview(QScrollArea):
    
    def __init__(self, parent, color):
        
        super(Preview, self).__init__(parent)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f'background: {color}')
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.setStyleSheet('''
            border: none;
            ''')
        self.setContentsMargins(0, 0, 0, 0)
        
    def show_image(self, index):
        
        self.verticalScrollBar().setSliderPosition(0)
        self.horizontalScrollBar().setSliderPosition(0)

        if index is None: pixmap = QPixmap()
        
        else:
            data = index.data(Qt.UserRole)
            path = data[0].pop()
            type_ = data[5].pop()
            if path.endswith(('.mp4', '.webm')): path = get_frame(path)

            pixmap = QPixmap(path)
            height, width = pixmap.width(), pixmap.height()
            aspect_ratio = (
                width / height 
                if height > width else
                height / width
                )

            if (type_ == 3 and aspect_ratio < .6) or aspect_ratio < .3: 
                if height < width:
                    pixmap.scaledToHeight(self.height())
                else: pixmap.scaledToWidth(self.width())
            else: pixmap = QPixmap(path).scaled(
                self.size(), Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )

        self.label.setPixmap(pixmap)

class Timer(QLabel):
    
    def __init__(self, parent):
        
        super(QLabel, self).__init__(parent)
        
        self.thread = Worker(self)
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
            self.thread.arguments = self.current.data(Qt.UserRole)
            self.thread.start()
            
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

class Worker(QThread):
    
    def __init__(self, parent):
        
        super(Worker, self).__init__(parent)

    def run(self):
    
        MYSQL.execute(GESTURE, (self.arguments,), commit=1)