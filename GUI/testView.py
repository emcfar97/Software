import os
import mysql.connector as sql
from PyQt5.QtGui import QPen, QPixmap, QImage
from PyQt5.QtCore import Qt, QSize, QRect, QSizeF, QRectF
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsWidget, QGraphicsScene, QGraphicsGridLayout, QGraphicsView, QGraphicsItem

DATAB = sql.connect(
    user='root', password='SchooL1@', database='userData', 
    host='192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
    )
CURSOR = DATAB.cursor()
SELECT = 'SELECT path FROM imageData WHERE path LIKE "%.jp%g" ORDER BY RAND()'

class RectWidget(QGraphicsWidget):

    def __init__(self, thumb_path, parent = None):

        QGraphicsWidget.__init__(self, parent)

        self.picdims = [110, 110]
        self.thumb_path = thumb_path
        self.pic = self.getpic(thumb_path)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self._boundingRect = QRect()
        
        self.setAcceptHoverEvents(True)

    def boundingRect(self):

        width = self.pic.rect().width()
        height = self.pic.rect().height()
        
        thumb_widget_rect = QRectF(0.0, 0.0, width, height)
        self._boundingRect = thumb_widget_rect

        return thumb_widget_rect

    def sizeHint(self, which, constraint = QSizeF()):

        return self._boundingRect.size()

    def getpic(self, path):

        if path.endswith(('.mp4', '.webm')):
                
            success, image = VideoCapture(path).read()
            image = QImage(
                image.data, image.shape[1], image.shape[0], 
                QImage.Format_RGB888
                ).rgbSwapped()
            
        else: image = QImage(path)

        image = image.scaled(
            *self.picdims, Qt.KeepAspectRatio, 
            transformMode=Qt.SmoothTransformation
            )
        
        return QPixmap.fromImage(image)  

    def paint(self, painter, option, widget):

        # Draw image
        painter.drawPixmap(QRect(
            0, 0 , 
            self.pic.rect().width(), 
            self.pic.rect().height()), 
            self.pic, 
            self.pic.rect()
            )
                     
    # def mousePressEvent(self, event):

    #     print('Widget Clicked')

    def mouseHoverEvent(self, event):

        print('Widget enter')

    def mouseReleaseEvent(self, event):

        print('Widget release')


class MainWindow(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)
        
        self.appname = "Moving Pictures"
        self.setObjectName('MainWindow')
        self.resize(800, 700)

        self.setWindowTitle(self.appname)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.panel = QGraphicsWidget()
        self.scene.addItem(self.panel)
        
        layout = QGraphicsGridLayout()
        layout.setContentsMargins(9, 9, 9, 9)
        self.panel.setLayout(layout)

        CURSOR.execute(SELECT)
        for num, (path,) in enumerate(CURSOR.fetchmany(250)):

            column = num % 5
            row = num // 5
            thumb_widget = RectWidget(path)
            layout.addItem(thumb_widget, row, column, 1, 1)
            layout.setColumnSpacing (column, 20)
            layout.setRowSpacing(row, 15)
            thumb_widget.setSelected(True)
        # print(self.view.selectedIndexes())
        self.setCentralWidget(self.view)
        self.view.show()

if __name__ == "__main__":

    app = QApplication([])
    app.setApplicationName("Pyqt Image gallery example")

    main = MainWindow()
    main.show()

    app.exec_()