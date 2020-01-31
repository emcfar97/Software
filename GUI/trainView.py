from random import randint
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QDrag
from PyQt5.QtCore import QMimeData
from . import *

TEST = 'SELECT path FROM imageData WHERE path LIKE "%jp%g" LIMIT {}'

class Training(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
        self.populate([
            'photographs',
            'illustrations',
            '3-dimensional'
            ])
     
    def configure_gui(self):
        
        resolution = self.parent().size()
        self.setGeometry(
            0, 0, 
            resolution.width(),  resolution.height()
            )  
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
    
    def create_widgets(self):
        
        # self.ribbon = Ribbon(self)
        self.ribbon = QWidget(self)
        self.ribbon.setFixedSize(self.width(), 100)
        self.ribbon.setStyleSheet('background: red')

        self.scroll_widget = QWidget(self)
        self.scroll_widget.setFixedSize(self.width(), 600)
        
        self.layout.addWidget(self.ribbon)
        self.layout.addWidget(self.scroll)
        self.scroll.setWidget(self.scroll_widget)
    
    def populate(self, classes): 
    
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        for class_ in classes:
            row = Row(self.scroll_widget, class_)
            layout.addWidget(row)

        self.scroll.setWidgetResizable(True)
        self.scroll.setLayout(layout)
    
class Ribbon(QWidget):
     
    def __init__(self, parent):
         
        super().__init__(parent)
        self.configure_gui()
        self.create_widgets()
     
    def configure_gui(self):
        
        size = self.parent().size()
        self.setGeometry(
            0, 0, size.width(), 50
        )
    
    def create_widgets(self):
        
        QLabel('text', self)
    
class Row(QWidget):
    
    def __init__(self, parent, title):
         
        super().__init__(parent)
        self.title = title
        self.configure_gui()
        self.create_widgets()
        self.setAcceptDrops(True)
     
    def configure_gui(self):
        
        size = self.parent().size()
        width = size.width()
        self.setFixedWidth(width)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
    
    def create_widgets(self):
        
        self.label = QLabel(f' {self.title}', self)
        self.selection = QHBoxLayout()
        self.selection.setSpacing(5)
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.selection)
        CURSOR.execute(TEST.format(randint(5, 15)))

        for path, in CURSOR.fetchall():
            
            self.selection.addWidget(DraggableLabel(self, path))
    
    def dragEnterEvent(self, sender):
      
        pass

    def dropEvent(self, sender):
        
        pass 

def get_hex():
    
    k = hex(randint(0, 255))[2:]
    for i in range(2 - len(k)):
        k += '0'
    return k

class DraggableLabel(QLabel):

    def __init__(self, parent, image):

        super().__init__(parent)
        self.setPixmap(QPixmap(image))    
        self.setFixedSize(120, 120)
    
    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):

        if not (event.buttons() & Qt.LeftButton):
            return
 
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
 
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.text())
        mimedata.setImageData(self.pixmap().toImage())

        drag.setMimeData(mimedata)
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(), self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction | Qt.MoveAction)
