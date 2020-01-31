import textwrap
from . import *
from PyQt5.QtCore import QAbstractTableModel, QVariant, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractScrollArea, QAbstractItemView
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

def open_database():
     
    datab = QSqlDatabase.addDatabase('QODBC')
    datab.setUserName('root')
    datab.setPassword('SchooL1@')
    datab.setDatabaseName('userData')
    datab.setHostName(
        '192.168.1.43' if __file__.startswith(('e:\\', 'e:/')) else '127.0.0.1'
        )
    datab.open()
     
    return datab

class imageView(QTableView):

    def __init__(self, parent):

        super().__init__(parent)
         
        self.table = Model(self, parent.width())   
        self.setModel(self.table)
        self.horizontalHeader().hide()      
        self.verticalHeader().hide() 

        self.doubleClicked.connect(self.open_slideshow)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContentsOnFirstShow
            )
        
    def total(self): return len(self.table.images)
    
    def populate(self):
        
        self.table.images = CURSOR.fetchall()
        self.table.rowsLoaded = 0
        self.table.layoutChanged.emit()
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

    def selectionChanged(self, select, deselect):
        
        if not self.table.images: return
        parent = self.parent().parent()
        select, deselect = select.indexes(), deselect.indexes()
        
        if parent.windowTitle() == 'Manage Data':
            image = select[0].data(Qt.UserRole) if select else None
            parent.preview.show_image(image)
            # image = select if select else self.selectedIndexes()
            # parent.preview.show_image(image[0].data(Qt.UserRole))
        
        self.parent().status.modify(
            self.total(), len(self.selectedIndexes())
            )

    def open_slideshow(self, index):

        parent = self.parent().parent()

        if parent.windowTitle() == 'Manage Data':

            parent.open_slideshow(
                (index.row() * 5) + index.column()
                )

class Model(QAbstractTableModel):

    def __init__(self, parent, width):

        QAbstractTableModel.__init__(self, parent)
        self.wrapper = textwrap.TextWrapper(width=70)
        self.size = int(width * .1899)
        self.images = []
        self.rowsLoaded = 0

    def flags(self, index):
        
        return (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
            )
    
    def rowCount(self, parent): return len(self.images) // 5     

    def columnCount(self, parent): return 5

    def data(self, index, role):

        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind > len(self.images): return QVariant()

        if role == Qt.DecorationRole:
    
            path = self.images[ind][0]
            if path.endswith(('.mp4', '.webm')):
                
                success, image = VideoCapture(path).read()
                image = QImage(
                    image.data, image.shape[1], image.shape[0], 
                    QImage.Format_RGB888
                    ).rgbSwapped()
                
            else: image = QImage(path)

            image = image.scaled(
                self.size, self.size, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            
            return QPixmap.fromImage(image)

        elif role == Qt.ToolTipRole:
            
            tag, art, rat, sta, = self.images[ind][1:]
            tags = self.wrapper.wrap(f'{tag.strip()}')
            rest = self.wrapper.wrap(
                f'Artist: {art} Rating: {rat} Stars: {sta}'
                )
            return '\n'.join(tags + rest)

        elif role == Qt.UserRole: return QVariant(self.images[ind][0])

        elif role == Qt.SizeHintRole: return QSize(self.size, self.size)

        return QVariant()
   
    # def canFetchMore(self, index):

    #     return self.rowsLoaded < len(self.images)

    # def fetchMore(self, index, batch=100):

    #     remainder = self.rowsLoaded - len(self.images)
    #     itemsToFetch = min(batch, remainder)
    #     self.beginInsertRows(
    #         QModelIndex(), self.rowsLoaded,
    #         self.rowsLoaded + itemsToFetch - 1
    #         )
    #     self.rowsLoaded += itemsToFetch
    #     self.endInsertRows()

class Test(QSqlTableModel):

    def __init__(self, parent, width):

        QSqlTableModel.__init__(self, parent)
        self.database = open_database()
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.setTable('imageData')
        self.setQuery(
            QSqlQuery('SELECT path, tags, artist, rating, stars FROM imageData')
            )

        self.wrapper = textwrap.TextWrapper(width=70)
        self.size = int(width * .188)
        self.images = []
        self.rowsLoaded = 0

    def flags(self, index):

        return (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
            )
    
    def rowCount(self, parent): return len(self.images) // 5     

    def columnCount(self, parent): return 5

    def data(self, index, role):

        ind = (index.row() * 5) + index.column()

        if not index.isValid() or ind > len(self.images): return QVariant()

        if role == Qt.DecorationRole:

            path = self.images[ind][0]
            if path.endswith(('.mp4', '.webm')):
                
                success, image = VideoCapture(path).read()
                image = QImage(
                    image.data, image.shape[1], image.shape[0], 
                    QImage.Format_RGB888
                    ).rgbSwapped()
                
            else: image = QImage(path)

            image = image.scaled(
                self.size, self.size, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
            
            return QPixmap.fromImage(image)

        elif role == Qt.ToolTipRole:
            
            tag, art, rat, sta, = self.images[ind][1:]
            tags = self.wrapper.wrap(f'{tag.strip()}')
            rest = self.wrapper.wrap(
                f'Artist: {art}Rating: {rat} Stars: {sta}'
                )
            return '\n'.join(tags + rest)

        elif role == Qt.UserRole: return QVariant(self.images[ind][0])

        elif role == Qt.SizeHintRole: return QSize(self.size, self.size)

        return QVariant()
   
    # def canFetchMore(self, index):

    #     return self.rowsLoaded < 1000

    # def fetchMore(self, index, batch=100):

    #     remainder = self.rowsLoaded - len(self.images)
    #     itemsToFetch = min(batch, remainder)
    #     self.beginInsertRows(
    #         QModelIndex(), self.rowsLoaded,
    #         self.rowsLoaded + itemsToFetch - 1
    #         )
    #     self.rowsLoaded += itemsToFetch
    #     self.endInsertRows()

class Select(QLabel):

    def __init__(self, image, size):
        
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)

        self.image = image
        
        if image.endswith(('.mp4', '.webm')):
            
            success, image = VideoCapture(image).read()
            pixmap = QImage(
                image, size, size, 
                image.shape[1] * 3, 
                QImage.Format_RGB888
                )
            
        else:
        
            pixmap = QPixmap(image).scaled(
                size, size, Qt.KeepAspectRatio, 
                transformMode=Qt.SmoothTransformation
                )
        
        self.setPixmap(pixmap)
