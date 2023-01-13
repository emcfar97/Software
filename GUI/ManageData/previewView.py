from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea

from GUI.utils import get_frame

class Preview(QScrollArea):
    
    def __init__(self, parent):
        
        super(Preview, self).__init__(parent)
        self.configure_gui()
        
    def configure_gui(self):
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.setMouseTracking(True)
        self.setStyleSheet('''
            border: none;
            ''')
        self.setContentsMargins(0, 0, 0, 0)
        
    def update(self, index=None):

        if not (index and (data := index.data(Qt.ItemDataRole.UserRole))):
            
            pixmap = QPixmap()
            self.label.setText('No image')
            self.label.setStyleSheet('font: 20x;')
        
        else:
            
            self.path = data[1]
            type_ = data[6]
            
            if self.path.endswith(('.mp4', '.webm')): 
                self.path = get_frame(self.path)

            if not (pixmap := QPixmap(self.path)).isNull():
                
                height, width = pixmap.height(), pixmap.width()
                aspect_ratio = (
                    width / height 
                    if height > width else
                    height / width
                    )

                if (type_ == 3 and aspect_ratio < .6) or aspect_ratio < .3:
                    if height > width:
                        pixmap = pixmap.scaledToWidth(
                            self.width() * .9, 
                            Qt.TransformationMode.SmoothTransformation
                            )
                    else:
                        pixmap = pixmap.scaledToHeight(
                            self.height() * .9, 
                            Qt.TransformationMode.SmoothTransformation
                            )
                else: pixmap = pixmap.scaled(
                    self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                    )
            
            else:
                self.label.setText('No image')
                self.setStyleSheet('font: 20x;')

        self.verticalScrollBar().setSliderPosition(0)
        self.horizontalScrollBar().setSliderPosition(0)
        self.label.setPixmap(pixmap)
    
    # def mouseMoveEvent(self, event):
        
    #     if self.path.endswith(('.gif', '.mp4', '.webm')):
            
    #         print('Preview')
            
    def keyPressEvent(self, event):
        
        self.parent().parent().keyPressEvent(event)