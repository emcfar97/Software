from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea

from GUI.utils import get_frame, get_path

class Preview(QScrollArea):
    
    def __init__(self, parent):
        
        super(Preview, self).__init__(parent)
        self.configure_gui()
        
    def configure_gui(self):
        
        self.path = ''
        self.pixmap = QPixmap()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setText('Select a file to preview')
        self.label.setStyleSheet('font: 20x; color: gray')
        
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.setMouseTracking(True)
        self.setStyleSheet('''
            border: none;
            ''')
        self.setContentsMargins(0, 0, 0, 0)
        
    def update(self, index=None):

        if not (index and (data := index.data(Qt.ItemDataRole.UserRole))):
            
            self.pixmap.fill()    
            self.label.setPixmap(self.pixmap)        
            self.label.setText('Select a file to preview')
            self.label.setStyleSheet('font: 20x; color: gray')
            
            return

        self.path = get_path(data[1])
        self.verticalScrollBar().setSliderPosition(0)
        self.horizontalScrollBar().setSliderPosition(0)
        
        # read image/video file
        if self.path.suffix == '.webp': self.pixmap.load(str(self.path))
        else: self.pixmap = self.pixmap.fromImage(get_frame(str(self.path)))

        # resize image
        if not self.pixmap.isNull():
            
            height, width = self.pixmap.height(), self.pixmap.width()
            aspect_ratio = (
                width / height 
                if height > width else
                height / width
                )
            # if image has specific ratio or is comic with specific ratio
            if aspect_ratio < .3 or (data[6] == 3 and aspect_ratio < .6):
                
                if height > width:
                    
                    self.label.setPixmap(self.pixmap.scaledToWidth(
                        int(self.width() * .9), 
                        Qt.TransformationMode.SmoothTransformation
                        ))
                else:
                    
                    self.label.setPixmap(self.pixmap.scaledToHeight(
                        int(self.height() * .9), 
                        Qt.TransformationMode.SmoothTransformation
                        ))
            else:
                self.label.setPixmap(self.pixmap.scaled(
                    self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                    ))
        
        else:
            
            self.pixmap.fill() 
            self.label.setPixmap(self.pixmap)
            self.label.setText('Select a file to preview')
            self.label.setStyleSheet('font: 20x; color: gray')
    
    # def mouseHoverEvent(self, event):
        
    #     if self.path.suffix('.webm'):
            
    #         print('Preview')
    
    def mouseDoubleClickEvent(self, event):
        ''

        if self.verticalScrollBar().isEnabled() or self.horizontalScrollBar().isEnabled():
        
            pixmap = QPixmap(self.path)
            
            if pixmap.height() != self.height():
                
                pixmap = pixmap.scaled(
                    self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                    )
            else:
                
                height, width = self.pixmap.height(), self.pixmap.width()
                
                if height > width:
                    
                    self.label.setPixmap(self.pixmap.scaledToWidth(
                        int(self.width() * .9), 
                        Qt.TransformationMode.SmoothTransformation
                        ))
                else:
                    
                    self.label.setPixmap(self.pixmap.scaledToHeight(
                        self.height() * .9, 
                        Qt.TransformationMode.SmoothTransformation
                        ))
            
    def keyPressEvent(self, event):
        
        self.parent().parent().keyPressEvent(event)