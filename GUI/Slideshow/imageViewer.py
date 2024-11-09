from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QTransform

from GUI.utils import get_frame

class imageViewer(QLabel):
    
    def __init__(self, parent):
        
        super(imageViewer, self).__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(
            int(self.parent().width() * .3), 
            int(self.parent().height() * .3)
            )
        self.pixmap = QPixmap()
    
    def update(self, path):
        
        if path: 
            
            # read image/video file
            if path.endswith('.webp'): self.pixmap.load(path)
            else: self.pixmap = self.pixmap.fromImage(get_frame(path))
            
            self.setPixmap(self.pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                ))
            
        else: self.no_image()

    def no_image(self):
    
        self.pixmap.fill() 
        self.setPixmap(self.pixmap)
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

            # index = parent.model.gallery[parent.index]
            # image = QImage(str(get_path(index[1])))
                   
            pixmap = self.pixmap.scaled(
                event.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                transformMode=Qt.TransformationMode.SmoothTransformation
                )
                
            self.setPixmap(pixmap)