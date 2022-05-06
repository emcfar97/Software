from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap, QTransform

from GUI.slideshow.controls import Controls

class imageViewer(QLabel):
    
    def __init__(self, parent):
        
        super(imageViewer, self).__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(
            int(self.parent().width() * .3), 
            int(self.parent().height() * .3)
            )
    
    def update(self, pixmap):
        
        if pixmap: self.setPixmap(pixmap)
        else: self.setPixmap(QPixmap())

    def no_image(self):

        self.setText('There are no images')
        self.setStyleSheet(f'''
            background: white; 
            font: 12px;
            color: black
            ''')

    def rotate(self, path, sign):

        QPixmap(path).transformed(
            QTransform().rotate(90 * sign), 
            Qt.TransformationMode.SmoothTransformation
            ).save(path)

    def resizeEvent(self, event):

        parent = self.parent().parent()

        if not parent.stack.currentIndex() and parent.model.gallery:

            index = parent.model.gallery[parent.index]
            image = QImage(index[0])
                   
            pixmap = QPixmap(image).scaled(
                event.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                )
                
            self.setPixmap(pixmap)