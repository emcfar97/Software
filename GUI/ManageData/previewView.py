from .. import get_frame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QScrollArea

class Preview(QScrollArea):
    
    def __init__(self, parent):
        
        super(Preview, self).__init__(parent)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.setStyleSheet('''
            border: none;
            ''')
        self.setContentsMargins(0, 0, 0, 0)
        
    def update(self, index=None):

        if not (index and (data := index.data(Qt.UserRole))):
            
            pixmap = QPixmap()
            # self.label.setText('No image')
            # self.label.setStyleSheet('font: 20x')
        
        else:
            path = data[0]
            type_ = data[5]
            if path.endswith(('.mp4', '.webm')): path = get_frame(path)

            pixmap = QPixmap(path)
            if not pixmap.isNull():
                height, width = pixmap.height(), pixmap.width()
                aspect_ratio = (
                    width / height 
                    if height > width else
                    height / width
                    )

                if (type_ == 3 and aspect_ratio < .6) or aspect_ratio < .3:
                    if height > width:
                        pixmap = pixmap.scaledToWidth(
                            int(self.width() * .9), Qt.SmoothTransformation
                            )
                    else:
                        pixmap = pixmap.scaledToHeight(
                            int(self.height() * .9), Qt.SmoothTransformation
                            )
                else: pixmap = pixmap.scaled(
                    self.size(), Qt.KeepAspectRatio, 
                    transformMode=Qt.SmoothTransformation
                    )
            
            # else:
                # self.label.setText('No image')
                # self.setStyleSheet('font: 20x')

        self.verticalScrollBar().setSliderPosition(0)
        self.horizontalScrollBar().setSliderPosition(0)
        self.label.setPixmap(pixmap)
    
    def keyPressEvent(self, event):
        
        self.parent().parent().keyPressEvent(event)